#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO
import unicodecsv
import os
import re
import requests
import simplejson as json
from . import nav
from .. import app
from .. import lastuser
from ..models import db, Event, Participant, Venue, Activity
from ..forms import NewEventForm, EditEventForm, EventLogoForm, WelcomeLogoForm, ConfirmSignoutForm, EventSyncForm, SelectActivityForm, ActivityCheckinForm
from ..helpers import levenshtein, upload, delete_upload
from pytz import utc, timezone
from datetime import datetime
from flask import request, flash, url_for, render_template, jsonify
from werkzeug import secure_filename
from baseframe.forms import render_redirect, ConfirmDeleteForm
from coaster.views import jsonp, load_model, load_models
from coaster.utils import make_name
from mechanize import ParseResponse, urlopen, urljoin, Browser, RobustFactory
from sqlalchemy.orm.exc import NoResultFound
from collections import defaultdict
from urllib import urlencode
from hashlib import md5
from base64 import b64encode

hideemail = re.compile('.{1,3}@')

@app.route('/event/new', methods=['GET', 'POST'])
@nav.init(
    parent='index',
    title="New Event"
    )
@lastuser.requires_permission('siteadmin')
def event_new():
    form = NewEventForm()
    if form.validate_on_submit():
        event = Event()
        event.options = form.options.data
        event.speaker_options = form.speaker_options.data
        event.crew_options = form.crew_options.data
        form.populate_obj(event)
        if event.event_logo:
            event.event_logo = upload(event.event_logo)
        if event.welcome_logo:
            event.welcome_logo = upload(event.welcome_logo, 'sponsors')
        db.session.add(event)
        try:
            db.session.commit()
            flash('Event added')
            return render_redirect(url_for('index'))
        except:
            flash('There was an issue in adding the event')
            pass
    return render_template('form.html', form=form, title=u"New Event", submit=u"Add", cancel_url=url_for('index'))

@app.route('/event/<event>/sync', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id': 'event'}, 'event')
@nav.init(
    parent='event',
    title="Sync Event",
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id}
    )
def sync_event(event):
    syncform = EventSyncForm()
    if request.method == 'GET' or not syncform.validate_on_submit():
        return render_template('form.html', form=syncform, title=u"Sync", submit=u"Sync Now")
    else:   
        browser = Browser(factory=RobustFactory())
        speakers = []
        speakers_fetched = False
        lastuser_loggedin = False
        eventframe_data = None
        ret = []
        if (event.funnel_space or event.eventframe_sync) and request.form.get('lastuser_username', None) and request.form.get('lastuser_password', None):
            browser.open("https://auth.hasgeek.com/login")
            browser.select_form(nr=1)
            form = browser.form
            form['username'] = request.form.get('lastuser_username')
            form['password'] = request.form.get('lastuser_password')
            browser.open(form.click())
            if browser.geturl() == "https://auth.hasgeek.com/login":
                flash("Problem logging into LastUser", "danger")
                return render_template('form.html', form=EventSyncForm(), title=u"Sync", submit=u"Sync Now")
            else:
                lastuser_loggedin = True

            if lastuser_loggedin and event.funnel_space:
                browser.open("https://funnel.hasgeek.com/login")
                ret.append("Fetching speakers")
                browser.open("https://funnel.hasgeek.com/{space}/json".format(space=event.funnel_space))
                funnel_data = json.loads(browser.response().read())
                for proposal in funnel_data['proposals']:
                    if proposal['confirmed']:
                        proposal['speaker'] = unicode(proposal['speaker'])
                        if u'(' in proposal['speaker']:
                            proposal['speaker'] = u'('.join(proposal['speaker'].split('(')[:-1]).strip().title()
                        speakers.append((proposal['speaker'], proposal['email']))
                speakers = list(set(speakers))
                speakers_fetched = True
                ret.append("There are %s speakers" % len(speakers))
                ret.append("Syncing venues from Funnel")
                try:
                    names = [venue['name'] for venue in funnel_data['venues']]
                    for venue in Venue.query.filter_by(event=event, from_funnel=True).filter(~Venue.name.in_(names)).all():
                        for activity in venue.activity:
                            db.session.delete(activity)
                        db.session.delete(venue)
                    db.session.commit()
                    ret.append("Deleted removed venues")
                except Exception as e:
                        ret.append("Error deleting removed venues: %s" % str(e))
                venues = dict()
                for venue in funnel_data['venues']:
                    try:
                        venues[venue['name']] = Venue.query.filter_by(name=venue['name'], event=event, from_funnel=True).one()
                        ret.append("Venue %s exists as %s" % (venue['title'], venues[venue['name']].title))
                    except NoResultFound:
                        try:
                            venues[venue['name']] = Venue(event=event, name=venue['name'], title=venue['title'], from_funnel=True)
                            db.session.add(venues[venue['name']])
                            db.session.commit()
                            ret.append("Added venue %s" % venue['title'])
                        except Exception as e:
                            ret.append("Error adding venue %s: %s" % (venue['title'], str(e)))
                for room in funnel_data['rooms']:
                    venues[room['name']] = venues[room['venue']]
                activity = defaultdict(list)
                for day_number, day in enumerate(funnel_data['schedule']):
                    for slot in day['slots']:
                        for session in slot['sessions']:
                            if session['room'] and session['room'] in venues:
                                if (day_number, day['date']) not in activity[session['room']]:
                                    activity[session['room']].append((day_number, day['date']))

                for venue, days in activity.iteritems():
                    try:
                        dates = [date for (day_number, date) in days]
                        Activity.query.filter_by(venue=venues[venue], from_funnel=True).filter(~Activity.date.in_(dates)).delete(synchronize_session=False)
                        ret.append("Deleted removed activity days for %s" % venues[venue].title)
                    except Exception as e:
                        ret.append("Error deleting removed activity days for %s: %s" % (venues[venue].title, str(e)))
                    for day_number, date in days:
                        try:
                            item = Activity.query.filter_by(venue=venues[venue], date=date, from_funnel=True).one()
                            ret.append("Activity on %s exists as %s" % (item.date, item.title))
                        except NoResultFound:
                            try:
                                item = Activity(venue=venues[venue], date=date, title="Day %s - %s" % (day_number + 1, venues[venue].title), from_funnel=True)
                                db.session.add(item)
                                db.session.commit()
                                ret.append("Added activity: %s on %s" % (item.title, item.date))
                            except Exception as e:
                                ret.append("Error adding activity %s: %s" % ("Day %s - %s" % (day_number + 1, venues[venue].title), str(e)))
                ret.append("Funnel sync complete")
            if lastuser_loggedin and event.eventframe_sync:
                ret.append("Fetching data from Eventframe")
                browser.open("https://eventframe.hasgeek.com/login")
                browser.open(event.eventframe_sync)
                eventframe_data = json.loads(browser.response().read())['attendees']
                ret.append("Fetched %s people from Eventframe" % len(eventframe_data))
        if app.config['DOATTEND_EMAIL'] in [None, ''] or app.config['DOATTEND_PASS'] in [None, ''] or event.doattend_id in [None, '']:
            return 'Data not available'
        uri = 'http://doattend.com/'
        forms = ParseResponse(urlopen(urljoin(uri, 'accounts/sign_in')))
        form = forms[0]
        form['account[email]'] = app.config['DOATTEND_EMAIL']
        form['account[password]'] = app.config['DOATTEND_PASS']
        urlopen(form.click())
        csv_data = urlopen(urljoin(uri, 'events/' + event.doattend_id + '/orders/registration_sheet.csv')).read()
        guests_csv = urlopen(urljoin(uri, 'events/' + event.doattend_id + '/orders/confirmed_guests.csv')).read()
        urlopen(urljoin(uri, 'accounts/sign_out'))
        f = StringIO.StringIO(csv_data)
        headers = [make_name(field).replace(u'-', u'').replace(u'\n', u'') for field in f.next().split(',')]
        users = unicodecsv.reader(f, delimiter=',')

        added = [0]
        failed = []
        updated = [0]
        deleted = 0
        tickets = []
        ret.append("Starting Participants")
        def process_ticket(user):
            user[columns['name']] = user[columns['name']].title()
            participant = Participant.query.filter_by(ticket_number=user[columns['ticket_number']].strip(), event_id=event.id, online_reg=True).first()
            if not participant:
                for p in Participant.query.filter_by(email=user[columns['email']].strip(), event_id=event.id).all():
                    if levenshtein(p.name, user[columns['name']].strip()) <= 3:
                        participant = p
                        break
            elif participant.email != user[columns['email']]:
                participant.image = 'LOAD'
            if not columns['name'] or user[columns['name']] == 'Cancelled' or user[columns['name']] == 'Not Attending':
                return
            new = participant is None
            if new:
                participant = Participant()
                participant.event_id = event.id
                participant.purchases = []
                participant.image = 'LOAD'
            else:
                if participant.purchases is None:
                    participant.purchases = []
                else:
                    participant.purchases = participant.purchases.split(', ')
            if 'order_id' in columns and columns['order_id'] and user[columns['order_id']]:
                user[columns['order_id']] = int(user[columns['order_id']])
            if columns['twitter'] and user[columns['twitter']] and '@' in user[columns['twitter']]:
                user[columns['twitter']] = user[columns['twitter']].strip().replace('@', '').strip()
            if columns['phone'] and user[columns['phone']]:
                user[columns['phone']] = user[columns['phone']].strip().replace(' ', '').replace('-','')
            for field in columns.keys():
                if columns[field]:
                    value = user[columns[field]]
                    if type(value) == unicode:
                        value = value.strip()
                    value = None if value == '*' or value == '' or value == 'empty' else value
                    if (new or (field != 'ticket_number' and getattr(participant, field))) and value != getattr(participant, field):
                        setattr(participant, field, value)
            if speakers_fetched and participant.speaker and (participant.name, participant.email) not in speakers:
                participant.speaker = False
            if (participant.name, participant.email) in speakers:
                participant.speaker = True
            if user[others['ticket_type']]:
                participant.purchases.append(user[others['ticket_type']].strip())
            if 'addons' in others and others['addons'] and user[others['addons']]:
                participant.purchases = participant.purchases + (user[others['addons']]).strip().split(',')
            for i, purchase in enumerate(participant.purchases):
                participant.purchases[i] = purchase.strip().replace(u'Apr 18 - 19', u'May 16 - 17').replace(u'Apr 16 - 17', u'May 14 - 15').replace(u'Apr 16 - 19', u'May 14 - 17')
            if u"T-shirt" in participant.purchases or u"Corporate" in participant.purchases:
                participant.purchased_tee = True
            participant.purchases = ', '.join(list(set(participant.purchases)))
            participant.online_reg = True
            if participant.ticket_number:
                tickets.append(participant.ticket_number)
            try:
                if new:
                    db.session.add(participant)
                db.session.commit()
                if new:
                    added[0] = added[0] + 1
                    ret.append("Added " + participant.name.encode('utf-8'))
                else:
                    updated[0] = updated[0] + 1
                    ret.append("Updated " + participant.name.encode('utf-8'))
            except Exception as e:
                ret.append("Error adding/updating " + participant.name.encode('utf-8') + ': ' + str(e))
                failed.append(participant.name.encode('utf-8') + '(' + participant.email.encode('utf-8') + '): ' + str(e))
                db.session.rollback()
        def indexof(name):
            try:
                return headers.index(name)
            except ValueError:
                return None
        columns = dict(
            ticket_number=indexof(u'ticketnumber'),
            name=indexof(u'name'),
            email=indexof(u'email'),
            company=indexof(u'company'),
            job=indexof(u'jobtitle'),
            city=indexof(u'city'),
            phone=indexof(u'phone'),
            twitter=indexof(u'twitterhandle'),
            regdate=indexof(u'date'),
            order_id=indexof(u'orderid')
            )
        others = dict(
            ticket_type=indexof(u'ticketname'),
            addons=indexof(u'addonspurchased')
            )

        for user in users:
            process_ticket(user)
        ret.append("Done with Participants")
        ret.append("Starting Guests")
        f = StringIO.StringIO(guests_csv)
        headers = [make_name(field).replace(u'-', u'').replace(u'\n', u'') for field in f.next().split(',')]
        users = unicodecsv.reader(f, delimiter=',')
        columns = dict(
            ticket_number=indexof(u'ticketnumber'),
            name=indexof(u'name'),
            email=indexof(u'email'),
            company=indexof(u'company'),
            job=indexof(u'jobtitle'),
            city=indexof(u'city'),
            phone=indexof(u'phone'),
            twitter=indexof(u'twitterhandle'),
            regdate=indexof(u'confirmedon')
            )
        others = dict(
            ticket_type=indexof(u'ticket')
            )
        for user in users:
            process_ticket(user)
        ret.append("Done with Guests")
        if eventframe_data:
            ret.append("Starting Eventframe RSVP data")
            columns = dict(
                ticket_number='ticket',
                name='ticket_name',
                email='ticket_email',
                phone='ticket_phone',
                company='ticket_company',
                job='ticket_jobtitle',
                city='ticket_city',
                twitter='ticket_twitter'
                )
            others = dict(
                ticket_type='ticket_type'
                )
            for user in eventframe_data:
                if user['status'] == "Y" and 'ticket' in user:
                    process_ticket(user)
            ret.append("Done with RSVPs")
        ret.append("Removing deleted tickets")
        participants = Participant.query.filter(~Participant.ticket_number.in_(tickets), Participant.online_reg==True, Participant.event_id==event.id).all()
        for participant in participants:
            try:
                db.session.delete(participant)
                db.session.commit()
                deleted = deleted + 1
                ret.append("Delete: " + participant.name.encode('utf-8'))
            except Exception as e:
                ret.append("Error deleting  " + participant.name.encode('utf-8') + ':' + e)
        ret.append("Deleting complete")

        for participant in Participant.query.filter_by(event=event, image='LOAD').all():
                ret.append("Loading gravatar image for %s" % ( participant.email))
                try:
                    response = requests.get(
                        "http://www.gravatar.com/avatar/" + md5(participant.email.lower()).hexdigest(),
                        params={'d': '404', 's': '400'})
                    if response.status_code == 404:
                        participant.image = None
                        ret.append('Image not present')
                    else:
                        participant.image = b64encode(response.content)
                        ret.append('Image loaded: %s' % participant.image)
                    db.session.commit()
                except Exception as e:
                    ret.append('Error: ' + str(e))

        return json.dumps(dict(
            added=added[0],
            updated=updated[0],
            deleted=deleted,
            failed=failed,
            trace=ret
            ))

@app.route('/event/<event>', methods=['GET'])
@lastuser.requires_permission('registrations')
@load_model(Event, {'id': 'event'}, 'event')
@nav.init(
    parent='index',
    title=lambda objects: objects['event'].name,
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id}
    )
def event(event):
    tz = timezone(app.config['TIMEZONE'])
    participants = Participant.query.filter_by(event_id=event.id).order_by('name').all()
    return render_template('participants.html', participants=participants, event=event, hideemail=hideemail, enumerate=enumerate,
        utc=utc, tz=tz)


@app.route('/event/<event>/participant/<participant>/signin', methods=['POST'])
@lastuser.requires_permission('registrations')
@load_models(
    (Event, {'id': 'event'}, 'event'),
    (Participant, {'id': 'participant'}, 'participant')
    )
def event_signin(event, participant):
    if participant.nfc_id is not None:
        return jsonify(status=False, message=u"This participant has already been assigned a badge.")
    else:
        nfc_id = unicode(request.form['nfc_id'])
        someone = Participant.query.filter_by(nfc_id=nfc_id, event_id=event.id).first()
        if someone:
            return jsonify(status=False, message=u"This badge is already assigned to %s" % someone.name)
        else:
            participant.nfc_id = nfc_id
            # participant.attended = True
            # participant.attend_date = datetime.utcnow()
            try:
                db.session.commit()
                return jsonify(status=True, message=u"The badge has been successfully assigned to %s" % participant.name)
            except:
                db.session.rollback()
                return jsonify(status=False, message=u"There was an error assigning this badge to %s" % participant.name)


@app.route('/event/<event>/participant/<participant>/status', methods=['GET'])
@load_models(
    (Event, {'id':'event'}, 'event'),
    (Participant, {'id':'participant'}, 'participant')
    )
@lastuser.requires_permission('registrations')
def participation_status(event, participant):
    return jsonify(attended=participant.attended, nfc_id=participant.nfc_id)


@app.route('/event/<event>/participant/<participant>/signout', methods=['POST'])
@load_models(
    (Event, {'id':'event'}, 'event'),
    (Participant, {'id':'participant'}, 'participant')
    )
@lastuser.requires_permission('registrations')
def event_signout(event, participant):
    # participant.attended = False
    participant.nfc_id = None
    # participant.attend_date = None
    db.session.commit()
    return jsonify(status=True)


@app.route('/event/<id>/edit', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id': 'id'}, 'event')
@nav.init(
    parent='event',
    title="Edit",
    objects=['event'],
    urlvars=lambda objects: {'id': objects['event'].id}
    )
def event_edit(event):
    form = EditEventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        event.options = form.options.data
        event.speaker_options = form.speaker_options.data
        event.crew_options = form.crew_options.data
        try:
            db.session.commit()
            flash("Edited event '%s'." % event.title, 'success')
            return render_redirect(url_for('index'), code=303)
        except:
            flash("Could not save event '%s'." % event.title, 'error')
    return render_template('form.html', form=form, title=u"Edit — " + event.title, submit=u"Save", cancel_url=url_for('index'))

@app.route('/event/<id>/editlogo', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id': 'id'}, 'event')
@nav.init(
    parent='event',
    title=lambda objects: "Update Event Logo: %s" % (objects['event'].name),
    objects=['event'],
    urlvars=lambda objects: {'id': objects['event'].id}
    )
def event_editlogo(event):
    form = EventLogoForm()
    if form.validate_on_submit():
        old_logo = event.event_logo
        form.populate_obj(event)
        if event.event_logo:
            event.event_logo = upload(event.event_logo)
        else:
            event.event_logo = None
        try:
            db.session.commit()
            flash("Updated logo for event '%s'." % event.name, 'success')
            event_with_old_logo = Event.query.filter_by(event_logo=old_logo).first()
            if event_with_old_logo is not None:
                delete_upload(old_logo)
            return render_redirect(url_for('index'), code=303)
        except:
            flash("Could not update logo for event '%s'." % event.title, 'error')
    return render_template('form.html', form=form, title=u"Update Logo — " + event.title, submit=u"Save", cancel_url=url_for('index'))


@app.route('/event/<id>/editwelcomelogo', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id': 'id'}, 'event')
@nav.init(
    parent='event',
    title=lambda objects: "Update Welcome Screen Sponsor Logo: %s" % (objects['event'].name),
    objects=['event'],
    urlvars=lambda objects: {'id': objects['event'].id}
    )
def event_edit_welcome_logo(event):
    form = WelcomeLogoForm()
    if form.validate_on_submit():
        old_logo = event.welcome_logo
        form.populate_obj(event)
        if event.welcome_logo:
            event.welcome_logo = upload(event.welcome_logo, 'sponsors')
        else:
            event.event_logo = None
        try:
            db.session.commit()
            flash("Updated logo for event '%s'." % event.name, 'success')
            event_with_old_logo = Event.query.filter_by(event_logo=old_logo).first()
            if event_with_old_logo is not None:
                delete_upload(old_logo, 'sponsors')
            return render_redirect(url_for('index'), code=303)
        except:
            flash("Could not update logo for event '%s'." % event.title, 'error')
    return render_template('form.html', form=form, title=u"Update Logo — " + event.title, submit=u"Save", cancel_url=url_for('index'))


@app.route('/event/<id>/delete', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id':'id'}, 'event')
@nav.init(
    parent='event',
    title="Confirm Delete",
    objects=['event'],
    urlvars=lambda objects: {'id': objects['event'].id}
    )
def event_delete(event):
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            db.session.delete(event)
            db.session.commit()
        return render_redirect(url_for('index'), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Delete '%s' ?" % (event.title),
        message=u"Do you really want to delete the event '%s'?" % (event.title))


@app.route('/event/<event>/checkin', methods=['GET', 'POST'])
@lastuser.requires_permission(['kioskadmin', 'registrations'])
@load_model(Event, {'id': 'event'}, 'event')
def event_nfc_checkin(event):
    if request.method == 'GET':
        checkin_for = None
        checkin_form = ActivityCheckinForm()
        if event.active:
            activity = event.activity(today=True)
            if len(activity) > 1:
                checkin_for = request.args.get('checkin_for') 
                for item in activity:
                    if item.id == checkin_for:
                        checkin_for = item
                        break
                if not checkin_for:
                    activity_form = SelectActivityForm()
                    activity_form.checkin_for.choices = [item.id for item in activity] 
                    return render_template('form.html', form=activity_form)
                else:
                    checkin_form.activity_id.data = checkin_for.id
            else:
                checkin_for = activity[0]
        return render_template('activity_checkin.html', event=event, checkin_for=checkin_for, checkin_form=checkin_form)
    else:
        if not event.active:
            return jsonify(status=False, msg="Event not active")
        participant = Participant.query.filter_by(nfc_id=request.form.get('nfc_id'), event=event).first() if request.form.get('nfc_id') else None
        if not participant:
            return jsonify(status=False, msg="You are not signed up for the event")
        activity = event.activity(today=True)
        def make_checkin(activity):
            name = participant.name.split(' ')
            name = name[0] if len(name[0]) > 3 else participant.name
            name = '<strong>%s</strong>' % name
            if activity.checkedin(participant):
                return jsonify(status=True, already=True, msg='<p>Hi %s!</p><p>You have already checked in for</p><p class="activity">%s</p>' % (name, activity.title), purchases=participant.purchases, image=("data:image/jpeg;base64,%s" % participant.image if participant.image and participant.image != 'LOAD' else None))
            else:
                activity.checkin(participant)
                return jsonify(status=True, already=False, msg='<p>Welcome %s!</p><p>Thanks for checking in at</p><p class="activity">%s</p>' % (name, activity.title), purchases=participant.purchases, image=("data:image/jpeg;base64,%s" % participant.image if participant.image and participant.image != 'LOAD' else None))
        if len(activity) == 1:
            return make_checkin(activity[0])
        else:
            checkin_for = request.form.get('checkin_for')
            if not checkin_for:
                return jsonify(status=False, msg="Please specify which activity to checkin for")
            else:
                for item in activity:
                    if item.id == checkin_for:
                        return make_checkin(item)
                return jsonify(status=False, msg="Incorrect activity specified")
