#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import nav
from .. import app
from .. import lastuser
from ..models import Event
import simplejson as json
from flask import render_template, g
from coaster.views import load_model

@app.route('/', methods=['GET'])
@nav.init(
    parent=None,
    title="Home"
    )
def index():
    events = Event.query.order_by('from_date desc, to_date desc').all()
    return render_template('index.html', events=events, siteadmin=lastuser.has_permission('siteadmin'), kioskadmin=lastuser.has_permission('kioskadmin'), registrations=lastuser.has_permission('registrations'))

@app.route('/ping', methods=['GET'])
def ping():
	return "1"

@app.route('/events.json')
def events_json():
	return json.dumps([dict(id=event.id, name=event.name) for event in Event.query.order_by('from_date desc, to_date desc').all()])