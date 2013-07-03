#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import app
from .. import lastuser
from ..models import db, Event, Participant
from ..forms import ParticipantForm
from datetime import datetime
from flask import request, flash, url_for, render_template
from coaster.views import load_model, jsonp

@app.route('/event/<id>/participant/new', methods=['GET', 'POST'])
@load_model(Event, {'id': 'id'}, 'event')
@lastuser.requires_permission('kioskadmin')
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


@app.route('/event/<event>/participant/<nfc_id>', methods=["GET"])
@lastuser.requires_permission('kioskadmin')
def get_participant(event, nfc_id):
        try:
            participant = Participant.query.filter_by(event_id=event, nfc_id=nfc_id).first()
            response = jsonp(id=participant.id,name=participant.name, email=participant.email,twitter=participant.twitter,nfc_id=participant.nfc_id)
        except:
            response = jsonp(error="invalid")
        return response


@app.route('/<eid>/search', methods=['POST'])
@load_model(Event,{'id':'eid'},'event')
@lastuser.requires_permission('kioskadmin')
def search(event, participants=None):
    query = request.form['key']
    participant = Participant.query.filter_by(event_id=event.id, ticket_number=int(query)).first()
    response = jsonp(ticket_number=participant.ticket_number, name=participant.name, email=participant.email)
    return response