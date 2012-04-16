#!/usr/bin/env python
# -*- coding: utf-8 -*-
from peopleflow import app
from flask import Flask, abort, request, render_template, redirect, url_for
from werkzeug import secure_filename
from flask import flash, session, g, Response
from coaster.views import load_model
from peopleflow.forms import EventForm
from peopleflow.models import db, Event, Participant
from peopleflow.views.login import lastuser
from dateutil import parser as dateparser
from pytz import utc, timezone
import os, csv, re
from datetime import datetime
from baseframe.forms import render_form, render_redirect, ConfirmDeleteForm
import time

hideemail = re.compile('.{1,3}@')

@app.route('/', methods=['GET'])
def index():
    events = Event.query.order_by('id').all()
    return render_template('index.html',events=events)

@app.route('/event/new', methods=['GET'])
@lastuser.requires_permission('siteadmin')
def event_new(eventform=None):
    if eventform is None:
        eventform = EventForm()
        print eventform
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
    reader = csv.reader(open(file,'rb'))
    # Skip the header
    reader.next()
    # Get the event
    event = Event.query.filter_by(year=year, name=eventname).first()
    for row in reader:
        participant = Participant()
        participant.ticket_number = row[0]
        participant.name = row[1]
        participant.email = row[2]
        participant.ticket_type = row[3]
        participant.company = row[4]
        participant.job = row[5]
        participant.city = row[6]
        participant.twitter = row[7]
        participant.tshirt_size = row[8]
        participant.regdate = dateparser.parse(row[9])
        participant.order_id = row[10]
        # participant.attended
        # participant.attenddate 
        participant.event_id = event.id
        db.session.add(participant)
        db.session.commit()        
    return redirect(url_for('index'))

@app.route('/<year>/<eventname>/upload', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
def event_upload(year,eventname):
    if request.method == 'GET':
        return render_template('upload.html')

    if request.method == 'POST':
        print "POST"
        file = request.files['file']
        # print file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print "here"
            flash("Uploaded "+filename)
            csv_populate(os.path.join(app.config['UPLOAD_FOLDER'], filename), year, eventname)
            return redirect(url_for('index'))


	
@app.route('/<year>/<eventname>/signin',methods=['GET','POST'])
def event_signin(eventname, year):
    if request.method=='GET':
        event = Event.query.filter_by(name=eventname, year=year).first()
        tz = timezone(app.config['TIMEZONE'])
        participants = Participant.query.filter_by(event_id=event.id).order_by('name').all()
        return render_template('participants.html',participants=participants,event=event, hideemail=hideemail, enumerate=enumerate,
            utc=utc, tz=tz)
    else:
        pid = request.form['id']
        participant = Participant.query.get(pid)
        if participant.attended:
            return "Already Signed in"
        else:
            nfc_id = unicode(request.form['nfc_id'])
            participant.nfc_id = nfc_id
            participant.attended=True
            participant.attend_date = datetime.utcnow()
            db.session.commit()
            return nfc_id


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
        return redirect(url_for('index'), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Confirm delete",
        message=u"Delete '%s' ?" % (event.title))

