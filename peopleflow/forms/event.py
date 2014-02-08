# -*- coding: utf-8 -*-

import wtforms
import wtforms.fields.html5
import simplejson as json
from baseframe.forms import Form

def set_none(self, field):
    if not field.data:
        field.data = None

class BadgeOptions(wtforms.Form):
    name_color = wtforms.TextField('Name Color', validators=[wtforms.validators.Length(max=7)])
    company_color = wtforms.TextField('Company & Job Color', validators=[wtforms.validators.Length(max=7)])
    twitter_color = wtforms.TextField('Twitter Color', validators=[wtforms.validators.Length(max=7)])
    topMargin = wtforms.IntegerField('Top Margin(in mm)')
    leftMargin = wtforms.IntegerField('Left Margin(in mm)')
    rightMargin = wtforms.IntegerField('Right Margin(in mm)')
    bottomMargin = wtforms.IntegerField('Bottom Margin(in mm)')
    validate_name_color = set_none
    validate_company_color = set_none
    validate_twitter_color = set_none

class EventForm(Form):
    title = wtforms.TextField('Title', validators=[wtforms.validators.Required('A title is required')])
    name = wtforms.TextField('Name', validators=[wtforms.validators.Required('A name is required')])
    from_date = wtforms.DateField('From', description="Format: YYYY-MM-DD", validators=[wtforms.validators.Required('Propose a from date')])
    to_date = wtforms.DateField('To', description="Format: YYYY-MM-DD", validators=[wtforms.validators.Required('Propose a to date')])
    venue = wtforms.TextField('Venue', validators=[wtforms.validators.Required('Venue information is required')])
    doattend_id = wtforms.TextField('Doattend Event ID')
    print_type = wtforms.fields.SelectField('Print Type', choices=[(u'badge', 'Badge'), (u'label', 'Label')], default=u"badge")

    options = wtforms.fields.FormField(BadgeOptions)