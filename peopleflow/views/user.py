#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import app
from flask import Flask, abort, request, render_template, redirect, url_for, make_response, jsonify
from werkzeug import secure_filename
from flask import flash, session, g, Response
from coaster.views import load_model, load_models, jsonp
from ..forms import EventForm, ConfirmSignoutForm, ParticipantForm, KioskForm
from ..models import db, Event, Participant, Kiosk
from .. import lastuser
from dateutil import parser as dateparser
from pytz import utc, timezone
import os, csv, re
from StringIO import StringIO
from datetime import datetime
from baseframe.forms import render_form, render_redirect, ConfirmDeleteForm
import time
from flask.ext.mail import Message
from markdown import markdown
from ..helpers.printlabel import printlabel
import urllib
import hashlib


@app.route('/event/<id>/participant/new', methods=['GET', 'POST'])
@load_model(Event, {'id': 'id'}, 'event')
def venue_signup(event, participantform=None):
    if request.method=='GET':
        if participantform is None:
            participantform = ParticipantForm()
        context = {'participantform':participantform, 'event': event, 'year':event.year}
        return render_template('new_participant.html', **context)

    if request.method=='POST':
        form = ParticipantForm()
        if form.validate_on_submit():
            participant = Participant()
            form.populate_obj(participant)
            participant.attended = True
            participant.attend_date = datetime.utcnow()
            participant.event_id = event.id
            db.session.add(participant)
            try:
                db.session.commit()
                # flash('Done')
                flash('Participant %s added.' % participant.name, 'success')
                return "success"
            except:
                return "fail"
        else:
            if request.is_xhr:
                return render_template('participantform.html', participantform=form, ajax_re_register=True)
            else:
                flash("Please check your details and try again.", 'error')
                return venue_signup(participantform=form)


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
            filename = os.path.join(app.config['STATIC_UPLOAD_FOLDER'], 'sponsors', hashlib.md5(file).hexdigest())
            with open(filename, 'wb') as f:
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

@app.route('/event/<event>/kiosk/<kiosk>', methods=['GET','POST'])
@load_models(
    (Event, {'id':'event'}, 'event'),
    (Kiosk, {'id': 'kiosk'}, 'kiosk')
    )
@lastuser.requires_permission('kioskadmin')
def kiosk(event, kiosk):
    if request.method=='GET':
        return render_template('kiosk.html', kiosk=kiosk, event=event)

@app.route('/subscribe/<kiosk>',methods=['GET', 'POST'])
def share(kiosk):
    if request.method=='POST':
        kiosk_name = unicode(kiosk)
        nfc_id = request.form['id']
        kiosk = Kiosk.query.filter_by(name=kiosk_name).first()
        participant = Participant.query.filter_by(nfc_id=nfc_id).first()
        # share = Share()
        # share.share_date = datetime.utcnow()
        # share.participant_id = participant
        if participant in kiosk.participants:
            # flash("Contact already shared",'error')
            return render_redirect(url_for('kiosk', name=kiosk.name), code=303)
        else:

            kiosk.participants.append(participant)
            # share.kiosk_id = kiosk.id
            db.session.commit()
            # flash("Contact Shared",'success')
            return render_redirect(url_for('kiosk', name=kiosk.name), code=303)

@app.route('/participant/<nfc_id>', methods=["GET"])
def get_participant(nfc_id):
        try:
            participant = Participant.query.filter_by(nfc_id=nfc_id).first()
            response = jsonp(name=participant.name, email=participant.email)
        except:
            response = jsonp(error="invalid")
        return response


@app.route('/kiosk/<id>/delete', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Kiosk, {'id':'id'}, 'kiosk')
def kiosk_delete(kiosk):
    form = ConfirmDeleteForm()
    event = Event.query.get(kiosk.event_id)
    if form.validate_on_submit():
        if 'delete' in request.form:
            db.session.delete(kiosk)
            db.session.commit()
        return render_redirect(url_for('event_kiosks', eventname=event.name), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Confirm delete",
        message=u"Delete '%s' ?" % (kiosk.company))

@app.route('/<year>/<eventname>/kiosks', methods=['GET'])
@lastuser.requires_permission('siteadmin')
def event_kiosks(year,eventname):
    event = Event.query.filter_by(name=eventname, year=year).first()
    kiosks= Kiosk.query.filter_by(event_id=event.id).all()
    return render_template('event_kiosks.html', kiosks=kiosks, event=event, enumerate=enumerate)

@app.route('/kiosk/<id>/export', methods=['GET'])
@load_model(Kiosk, {'id':'id'}, 'kiosk')
def export_kiosk(kiosk):
    participants = StringIO()
    fieldnames= ['Name', 'Email','Company', 'Job']
    writer = csv.DictWriter(participants, fieldnames=fieldnames, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for participant in kiosk.participants:
        writer.writerow({"Name":participant.name,
                        "Email": participant.email,
                        "Company":participant.company,
                        "Job":participant.job
                            })
    response = make_response(participants.getvalue())
    response.headers['Content-Type']='text/csv';'charset=utf-8'
    response.headers['Content-Disposition']='attachment; filename=participants.csv'
    return response


@app.route('/<eid>/search', methods=['POST'])
@load_model(Event,{'id':'eid'},'event')
def search(event, participants=None):
    query = request.form['key']
    participant = Participant.query.filter_by(event_id=event.id, ticket_number=int(query)).first()
    response = jsonp(ticket_number=participant.ticket_number, name=participant.name, email=participant.email)
    return response

@app.route('/<year>/<eventname>/connect', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'name':'eventname'}, 'event')
def connect(event):
    if request.method=='GET':
        return render_template('connect.html', event = event)

    if request.method == 'POST':
        participants = []
        ids = request.form['id']
        ids = set(ids.split(','))
        msg = Message("Hello from "+event.title)
        for id in ids:
            participant = Participant.query.filter_by(event_id=event.id, nfc_id=id).first()
            participants.append(participant)

        for participant in participants:
            exchange = []
            for other in participants:
                if other!=participant:
                    exchange.append(other)
            msg.body= render_template('connectemail.md', name= participant.name, participants=exchange, event=event)
            msg.recipients=[participant.email]
            mail.send(msg)
        flash("Email sent!", "success")
        return render_template('connect.html', event = event)


@app.route('/print_card', methods=['POST'])
def print_card():
    twitter_handle = request.form['twitter']
    name = request.form['name']
    try:
        printlabel(line1=name, line2=twitter_handle)
        return jsonify({'msg': 'success'})
    except:
        return jsonify({'msg': 'failed'})
