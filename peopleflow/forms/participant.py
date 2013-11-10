# -*- coding: utf-8 -*-

import wtforms
import wtforms.fields.html5
from baseframe.forms import Form
from ..models import Participant

class ParticipantForm(Form):

    name = wtforms.TextField(u'Name', description=u"Please enter full name of the Participant", validators=[wtforms.validators.Required('A name is required')])
    email = wtforms.fields.html5.EmailField(u'e-mail', validators=[wtforms.validators.Required('Please enter the email'), wtforms.validators.Email()])
    phone = wtforms.TextField(u'Phone')
    company = wtforms.TextField(u'Company')
    job = wtforms.TextField(u'Job Title')
    city = wtforms.TextField(u'City')
    twitter = wtforms.TextField(u'twitter handle', description=u"Twitter handle of the participant without the @ symbol")
    notes = wtforms.TextAreaField('Notes')
    nfc_id = wtforms.HiddenField('NFC', validators=[wtforms.validators.Required('Please check the NFC Reader')])

    def __init__(self, event):
        self.event = event
        super(ParticipantForm, self).__init__()

    def validate_email(self, field):
        if Participant.query.filter_by(email=field.data, event_id=self.event.id).first():
            raise wtforms.ValidationError(u'The email address %s already exists' % field.data)