#!/usr/bin/env python
# -*- coding: utf-8 -*-
from peopleflow import app
from flask import Flask, abort, request, render_template, redirect, url_for
from werkzeug import secure_filename
from flask import flash, session, g, Response
from peopleflow.forms import EventForm
from peopleflow.models import db, Event, Participant
from dateutil import parser as dateparser
from pytz import utc, timezone
import os, csv, re
from datetime import datetime

hideemail = re.compile('.{1,3}@')

@app.route('/', methods=['GET'])
def index():
    events = Event.query.order_by('id').all()
    return render_template('index.html',events=events)

@app.route('/event/new', methods=['GET'])
def event_new(eventform=None):
    if eventform is None:
        eventform = EventForm()
        print eventform
    context = {'eventform':eventform}
    return render_template('new_event.html', **context)   

@app.route('/event/new', methods=['POST'])
def event_submit():
    form = EventForm()
    if form.validate_on_submit():
        event = Event()
        form.populate_obj(event)
        db.session.add(event)
        db.session.commit()
        flash("Event added")
        return render_template('index.html')
    else:
        if request.is_xhr:
            return render_template('eventform.html', eventform=form, ajax_re_register=True)
        else:
            flash("Please check your details and try again.", 'error')
            return event_add(eventform=form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def csv_populate(file, eventname):
    reader = csv.reader(open(file,'rb'))
    # Skip the header
    reader.next()
    # Get the event
    event = Event.query.filter_by(name=eventname).first()
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

@app.route('/<eventname>/upload', methods=['GET', 'POST'])
def event_upload(eventname):
    if request.method == 'GET':
        return render_template('upload.html')

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("Uploaded "+filename)
            csv_populate(os.path.join(app.config['UPLOAD_FOLDER'], filename), eventname)
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
            participant.attended=True
            participant.attend_date = datetime.utcnow()
            db.session.commit()
            return "Signed in"


# @app.route('event/new', methods=['POST'])
# def event_submit():
