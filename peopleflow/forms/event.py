# -*- coding: utf-8 -*-

import wtforms
import wtforms.fields.html5
from baseframe.forms import Form

class EventForm(Form):
    title = wtforms.TextField('Title', validators=[wtforms.validators.Required('A title is required')])
    name = wtforms.TextField('Name', validators=[wtforms.validators.Required('A name is required')])
    from_date = wtforms.DateField('From', description="Format: YYYY-MM-DD", validators=[wtforms.validators.Required('Propose a from date')])
    to_date = wtforms.DateField('To', description="Format: YYYY-MM-DD", validators=[wtforms.validators.Required('Propose a to date')])
    venue = wtforms.TextField('Venue', validators=[wtforms.validators.Required('Venue information is required')])
    doattend_id = wtforms.TextField('Doattend Event ID')