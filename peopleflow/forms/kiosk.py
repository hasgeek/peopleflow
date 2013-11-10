# -*- coding: utf-8 -*-

import wtforms
import wtforms.fields.html5
from baseframe.forms import Form, RichTextField

from ..models import Event

class KioskEditForm(Form):
    name = wtforms.TextField('Kiosk Name', validators=[wtforms.validators.Required('A name is required')])
    company = wtforms.TextField('Company Name', description="Optional. You may want to leave this attribute empty if the name of the company is clear from the logo.")
    company_tag = wtforms.TextField('Company Tagline', description="Optional")
    tap_msg = wtforms.TextField('Tapping message', description='Optional. Please tap your badge to ____? Leave blank to use default message.')
    privacy_policy = RichTextField('Privacy Policy')

class KioskLogoForm(Form):
    company_logo = wtforms.TextField('Company Logo', description="Provide the URL for the image of the sponsor's logo.", validators=[wtforms.validators.Required('The logo is required'), wtforms.validators.URL(message="Please provide a valid URL")])

class KioskForm(KioskEditForm, KioskLogoForm):
    pass