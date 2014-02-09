#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO
import unicodecsv
import os
import re
import simplejson as json
from . import nav
from .. import app
from .. import lastuser
from ..models import db, Event, Participant
from ..forms import EventForm, ConfirmSignoutForm, EventSyncForm
from ..helpers import levenshtein
from pytz import utc, timezone
from datetime import datetime
from flask import request, flash, url_for, render_template, jsonify
from werkzeug import secure_filename
from baseframe.forms import render_redirect, ConfirmDeleteForm
from coaster.views import jsonp, load_model, load_models
from coaster.utils import make_name
from mechanize import ParseResponse, urlopen, urljoin, Browser, RobustFactory

hideemail = re.compile('.{1,3}@')

@app.route('/event/new', methods=['GET', 'POST'])
@nav.init(
    parent='index',
    title="New Event"
    )
@lastuser.requires_permission('siteadmin')
def event_new():
    form = EventForm()
    if form.validate_on_submit():
        event = Event()
        form.populate_obj(event)
        event.options = form.options.data
        event.speaker_options = form.speaker_options.data
        event.crew_options = form.crew_options.data
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
        if event.funnel_space and request.form.get('funnel_username', None) and request.form.get('funnel_password', None):
            browser.open("https://funnel.hasgeek.com/login")
            browser.select_form(nr=1)
            form = browser.form
            form['username'] = request.form.get('funnel_username')
            form['password'] = request.form.get('funnel_password')
            browser.open(form.click())
            if browser.geturl() == "https://auth.hasgeek.com/login":
                flash("Problem logging into Funnel", "danger")
                return render_template('form.html', form=EventSyncForm(), title=u"Sync", submit=u"Sync Now")
            else:
                speakers_fetched = True
            browser.open("https://funnel.hasgeek.com/{space}/json".format(space=event.funnel_space))
            for proposal in json.loads(browser.response().read())['proposals']:
                if proposal['confirmed']:
                    proposal['speaker'] = unicode(proposal['speaker'])
                    if u'(' in proposal['speaker']:
                        proposal['speaker'] = u'('.join(proposal['speaker'].split('(')[:-1]).strip().title()
                    speakers.append((proposal['speaker'], proposal['email']))
            speakers = list(set(speakers))
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
        ret = ["Starting Participants"]
        def process_ticket(user):
            user[columns['name']] = user[columns['name']].title()
            participant = Participant.query.filter_by(ticket_number=user[columns['ticket_number']].strip(), event_id=event.id, online_reg=True).first()
            if not participant:
                for p in Participant.query.filter_by(email=user[columns['email']].strip(), event_id=event.id).all():
                    if levenshtein(p.name, user[columns['name']].strip()) <= 3:
                        participant = p
                        break
            if not columns['name'] or user[columns['name']] == 'Cancelled':
                return
            new = participant is None
            if new:
                participant = Participant()
                participant.event_id = event.id
                participant.purchases = []
            else:
                if participant.purchases is None:
                    participant.purchases = []
                else:
                    participant.purchases = participant.purchases.split(', ')
            if columns['order_id'] and user[columns['order_id']]:
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
                    value = None if value == '*' or value == '' else value
                    if (new or (field != 'ticket_number' and getattr(participant, field))) and value != getattr(participant, field):
                        setattr(participant, field, value)
            if speakers_fetched and participant.speaker and (participant.name, participant.email) not in speakers:
                participant.speaker = False
            if (participant.name, participant.email) in speakers:
                participant.speaker = True
            if user[others['ticket_type']]:
                participant.purchases.append(user[others['ticket_type']].strip())
            if others['addons'] and user[others['addons']]:
                participant.purchases = participant.purchases + (user[others['addons']]).strip().split(',')
            for purchase in participant.purchases:
                purchase = purchase.strip()
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
        ret.append("Removing deleted tickets")
        participants = Participant.query.filter(~Participant.ticket_number.in_(tickets), Participant.online_reg==True, Participant.event_id==event.id).all()
        for participant in participants:
            try:
                db.session.delete(participant)
                db.session.commit()
                deleted = deleted + 1
                ret.append(participant.name.encode('utf-8'))
            except Exception as e:
                ret.append("Error deleting  " + participant.name.encode('utf-8') + ':' + e)
        ret.append("Deleting complete")

        return '<pre>' + '\n'.join(ret) + "\nAdded " + str(added[0]) + ", Updated " + str(updated[0]) + " & Deleted " + str(deleted) + "\nFailed: " + '\n' + '\n'.join(failed) + '</pre>'

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
            participant.attended = True
            participant.attend_date = datetime.utcnow()
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
    participant.attended = False
    participant.nfc_id = None
    participant.attend_date = None
    db.session.commit()
    return jsonify(status=True)

@app.route('/event/<id>/count', methods=['GET', 'POST'])
@load_model(Event, {'id': 'id'}, 'event')
def get_count(event):
    response = jsonp(signed=event.participants.filter_by(attended=True).count(), total=event.participants.count())
    return response


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
    form = EventForm(obj=event)
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

