# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from baseframe.forms import Form, RichTextField

from ..models import Event

def get_events():
    return Event.query.order_by('id').all()

class KioskForm(Form):

    name = wtf.TextField('Kiosk Name', validators=[wtf.Required('A name is required')])
    company = wtf.TextField('Company Name', description="Optional. You may want to leave this attribute empty if the name of the company is clear from the logo.")
    company_tag = wtf.TextField('Company Tagline', description="Optional")
    company_logo = wtf.TextField('Company Logo', description="Provide the URL for the image of the sponsor's logo.", validators=[wtf.Required('The logo is required'), wtf.URL(message="Please provide a valid URL")])
    tap_msg = wtf.TextField('Tapping message', description='Optional. Please tap your badge to ____? Leave blank to use default message.')
    privacy_policy = RichTextField('Privacy Policy')
    event = wtf.QuerySelectField('Select an event', query_factory= get_events, get_label='title', allow_blank=False)