#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import urllib
import hashlib
from StringIO import StringIO
from .. import app
from .. import lastuser
from ..models import db, Kiosk, Event, Participant, CXLog
from ..forms import KioskForm, ConfirmSignoutForm
from flask import request, flash, url_for, render_template, jsonify, make_response
from baseframe.forms import render_redirect, ConfirmDeleteForm
from coaster import make_name
from coaster.views import jsonp, load_model, load_models
from coaster.gfm import markdown
from flask.ext.mail import Mail, Message


@app.route('/event/<id>/kiosk/new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id':'id'}, 'event')
def kiosk_new(event, kioskform=None):
    if request.method == 'GET':
        if kioskform is None:
            kioskform = KioskForm()
        context = {'kioskform':kioskform, 'event':event}
        return render_template('new_kiosk.html', **context)

    if request.method == 'POST':
        form = KioskForm()
        if form.validate_on_submit():
            kiosk = Kiosk()
            form.populate_obj(kiosk)
            file = urllib.urlopen(kiosk.company_logo).read()
            filename = hashlib.md5(file).hexdigest()
            filepath = os.path.join(app.config['STATIC_UPLOAD_FOLDER'], 'sponsors', filename)
            with open(filepath, 'wb') as f:
                f.write(file)
                f.close()
            kiosk.company_logo = filename
            db.session.add(kiosk)
            db.session.commit()
            flash("Kiosk added")
            return render_redirect(url_for('index'), code=303)
        else:
            if request.is_xhr:
                return render_template('kioskform.html', kioskform=form, ajax_re_register=True)
            else:
                flash("Please check your details and try again.", 'error')
                return event_add(kioskform=form)

#TODO: Check for kiosk-event releationship when fetching kiosk
@app.route('/event/<event>/kiosk/<kiosk>', methods=['GET','POST'])
@load_models(
    (Event, {'id':'event'}, 'event'),
    (Kiosk, {'id': 'kiosk'}, 'kiosk')
    )
@lastuser.requires_permission('kioskadmin')
def kiosk(event, kiosk):
    if request.method=='GET':
        return render_template('kiosk.html', kiosk=kiosk, event=event)


#TODO: Check for kiosk-event and event-participant relationship
@app.route('/event/<event>/kiosk/<kiosk>/subscribe',methods=['GET', 'POST'])
@load_models(
    (Event, {'id':'event'}, 'event'),
    (Kiosk, {'id': 'kiosk'}, 'kiosk')
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
    (Event, {'id':'event'}, 'event'),
    (Kiosk, {'id': 'kiosk'}, 'kiosk')
    )
def kiosk_delete(event, kiosk):
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            db.session.delete(kiosk)
            db.session.commit()
        return render_redirect(url_for('event_kiosks', event=event.id), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Confirm delete",
        message=u"Delete '%s' ?" % (kiosk.company))

@app.route('/event/<event>/kiosks', methods=['GET'])
@lastuser.requires_permission('kioskadmin')
@load_models(
    (Event, {'id':'event'}, 'event')
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