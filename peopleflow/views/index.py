#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import app
from .. import lastuser
from ..models import Event
from flask import render_template, g

@app.route('/', methods=['GET'])
def index():
    events = Event.query.order_by('from_date desc, to_date desc, date desc').all()
    return render_template('index.html', events=events, siteadmin=lastuser.has_permission('siteadmin'), kioskadmin=lastuser.has_permission('kioskadmin'))