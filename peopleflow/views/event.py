#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import re
from .. import app
from .. import lastuser
from ..models import db, Event, Participant
from ..forms import EventForm, ConfirmSignoutForm
from pytz import utc, timezone
from datetime import datetime
from flask import request, flash, url_for, render_template, jsonify
from werkzeug import secure_filename
from baseframe.forms import render_redirect, ConfirmDeleteForm
from coaster.views import jsonp, load_model, load_models

hideemail = re.compile('.{1,3}@')

@app.route('/event/new', methods=['GET'])
@lastuser.requires_permission('siteadmin')
def event_new(eventform=None):
    if eventform is None:
        eventform = EventForm()
    context = {'eventform':eventform}
    return render_template('new_event.html', **context)

@app.route('/event/new', methods=['POST'])
@lastuser.requires_permission('siteadmin')
def event_submit():
    form = EventForm()
    if form.validate_on_submit():
        event = Event()
        form.populate_obj(event)
        db.session.add(event)
        db.session.commit()
        flash("Event added")
        return render_redirect(url_for('index'), code=303)
    else:
        if request.is_xhr:
            return render_template('eventform.html', eventform=form, ajax_re_register=True)
        else:
            flash("Please check your details and try again.", 'error')
            return event_add(eventform=form)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def csv_populate(file, year, eventname):
    reader = csv.reader(open(file,'rb'), dialect='excel', quotechar='|')
    # Skip the header
    reader.next()
    # Get the event
    event = Event.query.filter_by(year=year, name=eventname).first()
    # Get all the participants of the event
    participants = Participant.query.filter_by(event_id=event.id).all()
    duplicates = 0
    new = 0
    if participants:
        for row in reader:
            for participant in participants:
                if participant.ticket_number == int(row[0]):
                    duplicates = duplicates + 1
                    break
            else:
                new_participant = Participant()
                try:
                    participant.ticket_number = int(row[0])
                except ValueError:
                    participant.ticket_number = None
                new_participant.name = row[1]
                new_participant.email = row[2]
                new_participant.ticket_type = row[3]
                new_participant.company = row[4]
                new_participant.job = row[5]
                new_participant.city = row[6]
                new_participant.twitter = row[7]
                new_participant.tshirt_size = row[8]
                new_participant.regdate = dateparser.parse(row[9])
                try:
                    participant.order_id = int(row[10])
                except ValueError:
                    participant.order_id = None
                new_participant.event_id = event.id
                db.session.add(new_participant)
                db.session.commit()
                new = new + 1
    else:
        for row in reader:
            participant = Participant()
            try:
                participant.ticket_number = int(row[0])
            except ValueError:
                participant.ticket_number = None
            participant.name = row[1]
            participant.email = row[2]
            participant.ticket_type = row[3]
            participant.company = row[4]
            participant.job = row[5]
            participant.city = row[6]
            participant.twitter = row[7]
            participant.tshirt_size = row[8]
            participant.regdate = dateparser.parse(row[9])
            try:
                participant.order_id = int(row[10])
            except ValueError:
                participant.order_id = None
            participant.event_id = event.id
            db.session.add(participant)
            db.session.commit()
            new = new + 1

    flash("%d duplicates, %d new records." % (duplicates, new), 'success')
    return redirect(url_for('index'))


@app.route('/<year>/<eventname>/upload', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
def event_upload(year,eventname):
    if request.method == 'GET':
        return render_template('upload.html')

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("Uploaded " + filename)
            csv_populate(os.path.join(app.config['UPLOAD_FOLDER'], filename), year, eventname)
            return redirect(url_for('index'))


@app.route('/event/<event>', methods=['GET'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id': 'event'}, 'event')
def event(event):
    tz = timezone(app.config['TIMEZONE'])
    participants = Participant.query.filter_by(event_id=event.id).order_by('name').all()
    return render_template('participants.html', participants=participants, event=event, hideemail=hideemail, enumerate=enumerate,
        utc=utc, tz=tz)


@app.route('/event/<event>/signin', methods=['POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id': 'event'}, 'event')
def event_signin(event):
    pid = request.form['id']
    participant = Participant.query.get(pid)
    if participant.attended:
        return "Already Signed in"
    else:
        nfc_id = unicode(request.form['nfc_id'])
        participant.nfc_id = nfc_id
        participant.attended = True
        participant.attend_date = datetime.utcnow()
        try:
            db.session.commit()
            return "success"
        except:
            return "id_used"


@app.route('/event/<event>/signout/<participant>', methods=['POST'])
@load_models(
    (Event, {'id':'event'}, 'event'),
    (Participant, {'id':'participant'}, 'participant')
    )
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
def event_edit(event):
    if request.method=='GET':
        form = EventForm(obj=event)
        return event_new(eventform=form)
    if request.method=='POST':
        form = EventForm(obj=event)
        if form.validate_on_submit():
            form.populate_obj(event)
            db.session.commit()
            flash("Edited event '%s'." % event.title, 'success')
            return render_redirect(url_for('index'), code=303)
    return event_add(eventform=form)


@app.route('/event/<id>/delete', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id':'id'}, 'event')
def event_delete(event):
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            db.session.delete(event)
            db.session.commit()
        return render_redirect(url_for('index'), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Confirm delete",
        message=u"Delete '%s' ?" % (event.title))

