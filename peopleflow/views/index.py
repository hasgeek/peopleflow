#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import app
from flask import render_template
from ..models import Event

@app.route('/', methods=['GET'])
def index():
    events = Event.query.order_by('id').all()
    return render_template('index.html', events=events)