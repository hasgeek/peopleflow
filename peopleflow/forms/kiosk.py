# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from baseframe.forms import Form, RichTextField

from ..models import Event

class KioskEditForm(Form):
    name = wtf.TextField('Kiosk Name', validators=[wtf.Required('A name is required')])
    company = wtf.TextField('Company Name', description="Optional. You may want to leave this attribute empty if the name of the company is clear from the logo.")
    company_tag = wtf.TextField('Company Tagline', description="Optional")
    tap_msg = wtf.TextField('Tapping message', description='Optional. Please tap your badge to ____? Leave blank to use default message.')
    privacy_policy = RichTextField('Privacy Policy')

class KioskForm(KioskEditForm):
    company_logo = wtf.TextField('Company Logo', description="Provide the URL for the image of the sponsor's logo.", validators=[wtf.Required('The logo is required'), wtf.URL(message="Please provide a valid URL")])