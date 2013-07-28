#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import nav
from .. import app
from .. import lastuser
from ..models import Event
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