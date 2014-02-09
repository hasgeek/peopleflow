#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import urllib
import hashlib
from StringIO import StringIO
from . import nav
from .. import app
from .. import lastuser
from ..models import db, Kiosk, Event, Participant, CXLog
from ..forms import KioskForm, KioskEditForm, KioskLogoForm, ConfirmSignoutForm
from ..helpers.printlabel import printlabel, make_label_content
from flask import request, flash, url_for, render_template, jsonify, make_response
from baseframe.forms import render_redirect, ConfirmDeleteForm
from jinja2 import Markup
from coaster import make_name
from coaster.views import jsonp, load_model, load_models
from coaster.gfm import markdown
from flask.ext.mail import Mail, Message

def save_logo(url):
    file = urllib.urlopen(url).read()
    filename = hashlib.md5(file).hexdigest()
    filepath = os.path.join(app.config['STATIC_UPLOAD_FOLDER'], 'sponsors', filename)
    with open(filepath, 'wb') as f:
        f.write(file)
        f.close()
    return filename

def delete_logo(filename):
    os.remove(os.path.join(app.config['STATIC_UPLOAD_FOLDER'], 'sponsors', filename))

@app.route('/event/<id>/kiosk/new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id':'id'}, 'event')
@nav.init(
    parent='event_kiosks',
    title="New Kiosk",
    urlvars=lambda objects: {'id':objects['event'].id},
    objects = ['event']
    )
def kiosk_new(event):
    form = KioskForm()
    if form.validate_on_submit():
        kiosk = Kiosk()
        form.populate_obj(kiosk)
        kiosk.company_logo = save_logo(kiosk.company_logo)
        kiosk.event_id = event.id
        db.session.add(kiosk)
        try:
            db.session.commit()
            flash("Kiosk added")
            return render_redirect(url_for('event_kiosks', event=event.id))
        except:
            pass
    return render_template('form.html', form=form, title=u"New Kiosk — " + event.title, submit=u"Add", cancel_url=url_for('event_kiosks', event=event.id))

@app.route('/event/<event>/kiosk/<kiosk>/edit', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Kiosk, {'id': 'kiosk', 'event_id': 'event'}, 'kiosk'),
    (Event, {'id': 'event'}, 'event'),
    )
@nav.init(
    parent='event_kiosks',
    title=lambda objects: "Edit Kiosk: %s" % (objects['kiosk'].name),
    urlvars=lambda objects: {'event':objects['event'].id, 'kiosk':objects['kiosk'].id},
    objects = ['event', 'kiosk']
    )
def kiosk_edit(event, kiosk):
    form = KioskEditForm(obj=kiosk)
    if form.validate_on_submit():
        form.populate_obj(kiosk)
        try:
            db.session.commit()
            flash("Edited kiosk '%s'." % kiosk.name, 'success')
            return render_redirect(url_for('event_kiosks', event=event.id), code=303)
        except:
            flash("Could not save kiosk '%s'." % kiosk.name, 'error')
    return render_template('form.html', form=form, title=u"Edit — " + kiosk.name + u" —" + event.title, submit=u"Save", cancel_url=url_for('event_kiosks', event=event.id))

@app.route('/event/<event>/kiosk/<kiosk>/editlogo', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Kiosk, {'id': 'kiosk', 'event_id': 'event'}, 'kiosk'),
    (Event, {'id': 'event'}, 'event'),
    )
@nav.init(
    parent='event_kiosks',
    title=lambda objects: "Update Kiosk Logo: %s" % (objects['kiosk'].name),
    urlvars=lambda objects: {'event':objects['event'].id, 'kiosk':objects['kiosk'].id},
    objects = ['event', 'kiosk']
    )
def kiosk_editlogo(event, kiosk):
    form = KioskLogoForm()
    if form.validate_on_submit():
        old_logo = kiosk.company_logo
        form.populate_obj(kiosk)
        kiosk.company_logo = save_logo(kiosk.company_logo)
        try:
            db.session.commit()
            flash("Updated logo for kiosk '%s'." % kiosk.name, 'success')
            kiosk_with_old_logo = Kiosk.query.filter_by(company_logo=old_logo).first()
            if kiosk_with_old_logo is None:
                delete_logo(old_logo)
            return render_redirect(url_for('event_kiosks', event=event.id), code=303)
        except:
            flash("Could not update logo for kiosk '%s'." % kiosk.name, 'error')
    return render_template('form.html', form=form, title=u"Update Logo — " + kiosk.name + u" — " + event.title, submit=u"Save", cancel_url=url_for('event_kiosks', event=event.id))

@app.route('/event/<event>/kiosk/<kiosk>', methods=['GET','POST'])
@load_models(
    (Kiosk, {'id': 'kiosk', 'event_id': 'event'}, 'kiosk'),
    (Event, {'id':'event'}, 'event'),
    )
@lastuser.requires_permission('kioskadmin')
def kiosk(event, kiosk):
    if request.method=='GET':
        kiosk.privacy_policy = Markup(kiosk.privacy_policy)
        return render_template('kiosk.html', kiosk=kiosk, event=event)


@app.route('/event/<event>/kiosk/<kiosk>/subscribe',methods=['GET', 'POST'])
@load_models(
    (Kiosk, {'id': 'kiosk', 'event_id': 'event'}, 'kiosk'),
    (Event, {'id':'event'}, 'event'),
    )
@lastuser.requires_permission('kioskadmin')
def share(event, kiosk):
    if request.method=='POST':
        nfc_id = request.form['id']
        participant = Participant.query.filter_by(nfc_id=nfc_id).first()
        # share = Share()
        # share.share_date = datetime.utcnow()
        # share.participant_id = participant
        if participant not in kiosk.participants:
            kiosk.participants.append(participant)
            # share.kiosk_id = kiosk.id
            db.session.commit()
            # flash("Contact Shared",'success')
        return render_redirect(url_for('kiosk', kiosk=kiosk.id, event=event.id), code=303)

@app.route('/event/<event>/kiosk/<kiosk>/delete', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Kiosk, {'id': 'kiosk', 'event_id': 'event'}, 'kiosk'),
    (Event, {'id':'event'}, 'event'),
    )
@nav.init(
    parent='event_kiosks',
    title=lambda objects: "Confirm Delete of Kiosk: %s" % (objects['kiosk'].name),
    urlvars=lambda objects: {'event':objects['event'].id, 'kiosk':objects['kiosk'].id},
    objects = ['event', 'kiosk']
    )
def kiosk_delete(event, kiosk):
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            db.session.delete(kiosk)
            db.session.commit()
        return render_redirect(url_for('event_kiosks', event=event.id), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Delete '%s' ?" % (kiosk.name),
        message=u"Do you really want to delete the kiosk '%s' from event %s?" % (kiosk.name, event.title))

@app.route('/event/<event>/kiosks', methods=['GET'])
@lastuser.requires_permission('kioskadmin')
@load_models(
    (Event, {'id':'event'}, 'event')
    )
@nav.init(
    parent='event',
    title="ContactPoint Kiosks",
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id}
    )
def event_kiosks(event):
    return render_template('event_kiosks.html', event=event, siteadmin=lastuser.has_permission('siteadmin'), kioskadmin=lastuser.has_permission('kioskadmin'))

@app.route('/event/<event>/kiosk/<kiosk>/export', methods=['GET'])
@load_model(Kiosk, {'id':'kiosk', 'event_id': 'event'}, 'kiosk')
@lastuser.requires_permission('siteadmin')
def export_kiosk(kiosk):
    participants = StringIO()
    fieldnames= ['Name', 'Email','Company', 'Job', 'Phone', 'City']
    writer = csv.DictWriter(participants, fieldnames=fieldnames, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for participant in kiosk.participants:
        writer.writerow({"Name":participant.name,
                        "Email": participant.email,
                        "Company": participant.company,
                        "Job": participant.job,
                        "Phone": participant.phone,
                        "City": participant.city
                            })
    response = make_response(participants.getvalue())
    response.headers['Content-Type']='text/csv';'charset=utf-8'
    response.headers['Content-Disposition']='attachment; filename=participants.csv'
    return response

@app.route('/event/<event>/contact_exchange', methods=['GET','POST'])
@lastuser.requires_permission('kioskadmin')
@load_model(Event, {'id':'event'}, 'event')
def contact_exchange(event):
    if request.method=='GET':
        return render_template('contact_exchange.html', event=event, debug=str(app.config['DEBUG']).lower(), ui_test=str(request.args.get('ui_test', False)).lower())

    if request.method == 'POST':
        ids = tuple(request.form.getlist('ids[]'))
        if len(ids) < 2:
            return jsonify(status=False, error=u'Insufficient users to connect')
        users = Participant.query.filter(Participant.event_id == event.id, Participant.nfc_id.in_(ids)).all()
        mail = Mail(app)
        message = Message("You connected with " + str(len(users) - 1) + " people using ContactExchange")
        message.cc = list()
        for user in users:
            email = '"' + user.name + '"<' + user.email + '>'
            if message.reply_to is None:
                message.reply_to = email
                message.add_recipient(email)
            else:
                message.cc.append(email)
            message.attach(make_name(user.name) + '.vcf', 'text/vcard', render_template('user_card.vcf', user=user, event=event))

        message.sender = '"HasGeek"<no-reply@hasgeek.com>'
        message.body = render_template('connectemail.md', users=users, event=event)
        message.html = markdown(message.body)
        log = CXLog()
        try:
            mail.send(message)
            log.sent = True
            log.log_message = u"Mail delivered to postfix server"
        except Exception as error:
            log.sent = True
            log.log_message = unicode(error)
        log.users = u','.join(ids)
        db.session.add(log)
        db.session.commit()
        return jsonify(success=True)

@app.route('/event/<event>/assign_badges', methods=['GET','POST'])
@lastuser.requires_permission('registrations')
@load_model(Event, {'id':'event'}, 'event')
def assign_badges(event):
    if request.method=='GET':
        return render_template('assign_badges.html', event=event)
    if request.method == 'POST':
        nfc_id = request.form['nfc_id']
        someone = Participant.query.filter_by(event_id=event.id, nfc_id=nfc_id).first()
        if someone:
            return jsonify(message=u"This badge is already assigned to %s.<br><small>Purchases: %s</small>" % (someone.name, someone.purchases), alert=u"error")
        orphan = Participant.query.filter_by(event_id=event.id, nfc_id=None).order_by(Participant.name.asc())[0]
        if orphan:
            orphan.nfc_id = nfc_id
            try:
                db.session.commit()
                if 'PRINTER_NAME' in app.config:
                    options = dict(event.options)
                    if orphan.speaker:
                        options.update(dict((option, value) for option, value in event.speaker_options.iteritems() if value))
                    elif 'Crew' in orphan.purchases:
                        options.update(dict((option, value) for option, value in event.crew_options.iteritems() if value))
                    printlabel(app.config['PRINTER_NAME'], event.print_type, make_label_content(orphan), options)
                return jsonify(message=u"This badge has been assigned to %s%s.<br><small>Purchases: %s</small>" % (orphan.name, u" from " + orphan.company if orphan.company else "", orphan.purchases), alert=u"success")
            except:
                db.session.rollback()
                return jsonify(message=u"There was an error assigning this badge to %s" % orphan.name, alert=u"error")
        else:
            return jsonify(message=u"Yo! There are no more unassigned participants to be assigned a badge!", alert=u"warning")

@app.route('/event/<event>/badge_stats', methods=['GET'])
@lastuser.requires_permission('registrations')
@load_model(Event, {'id':'event'}, 'event')
def badge_stats(event):
    total = Participant.query.filter_by(event_id=event.id)
    unassigned = total.filter_by(nfc_id=None).count()
    total = total.count()
    return jsonify(total=total, assigned=total-unassigned, unassigned=unassigned)
