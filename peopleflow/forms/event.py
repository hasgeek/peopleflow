# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from baseframe.forms import Form

class EventForm(Form):
    title = wtf.TextField('Title', validators=[wtf.Required('A title is required')])
    name = wtf.TextField('Name', validators=[wtf.Required('A name is required')])
    from_date = wtf.DateField('From', description="Format: YYYY-MM-DD", validators=[wtf.Required('Propose a from date')])
    to_date = wtf.DateField('To', description="Format: YYYY-MM-DD", validators=[wtf.Required('Propose a to date')])
    venue = wtf.TextField('Venue', validators=[wtf.Required('Venue information is required')])
    doattend_id = wtf.TextField('Doattend Event ID')