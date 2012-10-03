#!/usr/bin/env python
# -*- coding: utf-8 -*-
from peopleflow import app, mail
from flask import Flask, abort, request, render_template, redirect, url_for, make_response
from werkzeug import secure_filename
from flask import flash, session, g, Response
from coaster.views import load_model, jsonp
from peopleflow.forms import EventForm, ConfirmSignoutForm, ParticipantForm, KioskForm
from peopleflow.models import db, Event, Participant, Kiosk
from peopleflow.views.login import lastuser
from dateutil import parser as dateparser
from pytz import utc, timezone
import os, csv, re
from StringIO import StringIO
from datetime import datetime
from baseframe.forms import render_form, render_redirect, ConfirmDeleteForm
import time
from flask.ext.mail import Message
from markdown import markdown


hideemail = re.compile('.{1,3}@')
tz = timezone(app.config['TIMEZONE'])


@app.route('/', methods=['GET'])
def index():
    events = Event.query.order_by('id').all()
    return render_template('index.html',events=events)

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
    reader = csv.reader(open(file,'rb'))
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
                    duplicates = duplicates+1
                    break
            else:
                new_participant = Participant()
                new_participant.ticket_number = row[0]
                new_participant.name = row[1]
                new_participant.email = row[2]
                new_participant.ticket_type = row[3]
                new_participant.company = row[4]
                new_participant.job = row[5]
                new_participant.city = row[6]
                new_participant.twitter = row[7]
                new_participant.tshirt_size = row[8]
                new_participant.regdate = dateparser.parse(row[9])
                new_participant.order_id = row[10]
                new_participant.event_id = event.id
                db.session.add(new_participant)
                db.session.commit()
                new= new+1
    else:
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
            participant.event_id = event.id
            db.session.add(participant)
            db.session.commit()
            new = new+1

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
            flash("Uploaded "+filename)
            csv_populate(os.path.join(app.config['UPLOAD_FOLDER'], filename), year, eventname)
            return redirect(url_for('index'))


	
@app.route('/<year>/<eventname>/signin',methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
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
            try:
                db.session.commit()
                return "success"
            except:
                return "id_used"
                 
@app.route('/<year>/<eventname>/<pid>/signout', methods=['GET', 'POST'])
# @load_model(Participant, {'id':'id'}, 'participant')
def event_signout(year, eventname, pid):
    # pid = request.form['id']
    participant = Participant.query.get(pid)
    form = ConfirmSignoutForm()
    if form.validate_on_submit():
        if 'signout' in request.form:
            participant.attended=False
            participant.nfc_id= None
            participant.attend_date = None
            db.session.commit()
        return redirect(url_for('event_signin', year=year, eventname=eventname), code=303)
    return render_template('signout.html', form=form, title=u"Confirm card unassignment",
        message=u"Unassign card for '%s' ?" % (participant.name))

@app.route('/event/<id>/count', methods=['GET', 'POST'])
@load_model(Event, {'id': 'id'}, 'event')
def get_count(event):
    response = jsonp(signed=event.participants.filter_by(attended=1).count(), total=event.participants.count())
    return response



@app.route('/event/<id>/participant/new', methods=['GET', 'POST'])
@load_model(Event, {'id': 'id'}, 'event')
def venue_signup(event, participantform=None):
    if request.method=='GET':
        if participantform is None:
            participantform = ParticipantForm()
        context = {'participantform':participantform, 'eventname':event.name, 'year':event.year}
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


@app.route('/kiosk/new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
def kiosk_new(kioskform=None):
    if request.method == 'GET':
        if kioskform is None:
            kioskform = KioskForm()
        context = {'kioskform':kioskform}
        return render_template('new_kiosk.html', **context)   

    if request.method == 'POST':
        form = KioskForm()
        if form.validate_on_submit():
            kiosk = Kiosk()
            form.populate_obj(kiosk)
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

@app.route('/kiosk/<name>', methods=['GET','POST'])
@lastuser.requires_permission('kioskadmin')
def kiosk(name):
    if request.method=='GET':
        name = unicode(name)
        kiosk = Kiosk.query.filter_by(name=name).first()
        return render_template('kiosk.html', kiosk = kiosk)
    
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
            flash("Contact already shared",'error')
            return render_redirect(url_for('kiosk', name=kiosk.name), code=303)
        else:

            kiosk.participants.append(participant)
            # share.kiosk_id = kiosk.id
            db.session.commit()
            flash("Contact Shared",'success')
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






