# -*- coding: utf-8 -*-

import flask.ext.wtf as wtf
from baseframe.forms import Form
from ..models import Participant

class ParticipantForm(Form):

    name = wtf.TextField(u'Name', description=u"Please enter full name of the Participant", validators=[wtf.Required('A name is required')])
    email = wtf.TextField(u'e-mail', validators=[wtf.Required('Please enter the email')])
    phone = wtf.TextField(u'Phone')
    company = wtf.TextField(u'Company')
    job = wtf.TextField(u'Job Title')
    city = wtf.TextField(u'City')
    twitter = wtf.TextField(u'twitter handle', description=u"Twitter handle of the participant without the @ symbol")
    notes = wtf.TextAreaField('Notes')
    nfc_id = wtf.HiddenField('NFC', validators=[wtf.Required('Please check the NFC Reader')])

    def __init__(self, event):
        self.event = event
        super(ParticipantForm, self).__init__()

    def validate_email(self, field):
        if Participant.query.filter_by(email=field.data, event_id=self.event.id).first():
            raise wtf.ValidationError(u'The email address %s already exists' % field.data)