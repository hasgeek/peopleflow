#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import nav
from .. import app
from .. import lastuser
from ..models import db, Event, Participant
from ..forms import ParticipantForm
from ..helpers.printlabel import printlabel, make_label_content
from datetime import datetime, timedelta
from time import strftime
from flask import request, flash, url_for, render_template, jsonify
from coaster.views import load_model, load_models, jsonp
from baseframe.forms import render_redirect
from wtforms import SelectMultipleField, widgets

def add_new_participant(event):
    class Part(ParticipantForm):
        pass
    day_count = (event.to_date - event.from_date).days + 1
    options = [
        (u'Crew', u'Crew'),
        (u'On the spot - All days', u'On the spot - All days'),
        ]
    for single_date in [d for d in (event.from_date + timedelta(n) for n in range(day_count)) if d <= event.to_date]:
        options.append((u'On the spot - ' + strftime("%Y-%m-%d", single_date.timetuple()), u'On the spot - ' + strftime("%Y-%m-%d", single_date.timetuple())))
    Part.purchases = SelectMultipleField(u'Purchases',
        choices=options,
        coerce=unicode,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
        )
    form = Part(event)
    if form.validate_on_submit():
        participant = Participant()
        form.populate_obj(participant)
        someone = Participant.query.filter_by(nfc_id=participant.nfc_id, event_id=event.id).first()
        if someone:
            flash(u'This badge is already assigned to %s' % someone.name, 'error')
            return render_template('new_participant.html', form=form, event=event)
        participant.phone = participant.phone.replace(' ','').replace('-','').strip()
        participant.twitter = participant.twitter.replace('@','').strip()
        participant.purchases = u','.join(participant.purchases)
        participant.attended = True
        participant.online_reg = False
        participant.attend_date = datetime.utcnow()
        participant.event_id = event.id
        db.session.add(participant)
        try:
            db.session.commit()
            flash(u'Participant %s added.' % participant.name, 'success')
            return render_redirect(url_for('event', event=event.id))
        except:
            pass
    return render_template('new_participant.html', form=form, event=event)

@app.route('/event/<id>/participant/new', methods=['GET', 'POST'])
@load_model(Event, {'id': 'id'}, 'event')
@lastuser.requires_permission('registrations')
@nav.init(
    parent='event',
    title="New Participant",
    urlvars=lambda objects: {'id':objects['event'].id},
    objects = ['event']
    )
def venue_signup(event, participantform=None):
    return add_new_participant(event)


@app.route('/event/<event>/participant/<nfc_id>', methods=["GET"])
@lastuser.requires_permission(['kioskadmin', 'registrations'])
def get_participant(event, nfc_id):
        try:
            participant = Participant.query.filter_by(event_id=event, nfc_id=nfc_id).first()
            response = jsonp(id=participant.id,name=participant.name, email=participant.email,twitter=participant.twitter,nfc_id=participant.nfc_id)
        except:
            response = jsonp(error="invalid")
        return response

@app.route('/event/<event>/participant/<participant>/print_card', methods=['POST'])
@lastuser.requires_permission(['kioskadmin', 'registrations'])
@load_models(
    (Participant, {'event_id': 'event', 'id': 'participant'}, 'participant')
    )
def print_card(participant):
    try:
        if 'PRINTER_NAME' in app.config:
            printlabel(app.config['PRINTER_NAME'], make_label_content(participant))
            return jsonify(status=True, msg=u"Label for %s queued for printing" % participant.name)
        else:
            return jsonify(status=False, msg=u"Printer not configured")
    except:
        return jsonify(status=False, msg=u"There was an error in printing the label for %s" % participant.name)

@app.route('/<eid>/search', methods=['POST'])
@load_model(Event,{'id':'eid'},'event')
@lastuser.requires_permission('registrations')
def search(event, participants=None):
    query = request.form['key']
    participant = Participant.query.filter_by(event_id=event.id, ticket_number=int(query)).first()
    response = jsonp(ticket_number=participant.ticket_number, name=participant.name, email=participant.email)
    return response