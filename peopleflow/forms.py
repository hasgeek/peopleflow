#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from peopleflow.models import Event, Participant
from flask.ext.wtf import (
    Form,
    TextField,
    Required,
    URL,
    DateField,
    SubmitField,
    HiddenField,
    QuerySelectField,
    ValidationError,
    Label,
    Flags,
    SelectMultipleField,
    TextAreaField
    )


class EventForm(Form):

    name = TextField('Name', validators=[Required('A name is required')])
    title = TextField('Title', validators=[Required('A title is required')])
    from_date = DateField('From', description="Format: YYYY-MM-DD", validators=[Required('Propose a from date')])
    to_date = DateField('To', description="Format: YYYY-MM-DD", validators=[Required('Propose a to date')])
    venue = TextField('Venue', validators=[Required('Venue information is required')])
    doattend_id = TextField('Doattend Event ID')


class ConfirmSignoutForm(Form):
    """
    Confirm a delete operation
    """
    # The labels on these widgets are not used. See delete.html.
    delete = SubmitField(u"Sign out")
    cancel = SubmitField(u"Cancel")

class ParticipantForm(Form):

    name = TextField(u'Name', description=u"Please enter full name of the Participant", validators=[Required('A name is required')])
    email = TextField(u'e-mail', validators=[Required('Please enter the email')])
    phone = TextField(u'Phone')
    company = TextField(u'Company')
    job = TextField(u'Job Title')
    city = TextField(u'City')
    twitter = TextField(u'twitter handle', description=u"Twitter handle of the participant without the @ symbol")
    notes = TextAreaField('Notes')
    nfc_id = HiddenField('NFC', validators=[Required('Please check the NFC Reader')])

    def __init__(self, event):
        self.event = event
        super(ParticipantForm, self).__init__()

    def validate_email(self, field):
        if Participant.query.filter_by(email=field.data, event_id=self.event.id).first():
            raise ValidationError(u'The email address %s already exists' % field.data)


def get_events():
    return Event.query.order_by('id').all()


class KioskForm(Form):

    name = TextField('Kiosk Name', validators=[Required('A name is required')])
    company = TextField('Company Name', description="Optional. You may want to leave this attribute empty if the name of the company is clear from the logo.")
    company_tag = TextField('Company Tagline', description="Optional")
    company_logo = TextField('Company Logo', description="Provide the URL for the image of the sponsor's logo.", validators=[Required('The logo is required'), URL(message="Please provide a valid URL")])
    tap_msg = TextField('Tapping message', description='Optional. Please tap your badge to ____? Leave blank to use default message.')
    event = QuerySelectField('Select an event', query_factory= get_events, get_label='title', allow_blank=False)
