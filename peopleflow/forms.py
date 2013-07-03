#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from peopleflow.models import Event
from flask.ext.wtf import (
    Form,
    TextField,
    Required,
    URL,
    DateField,
    SubmitField,
    HiddenField,
    QuerySelectField,
    )


class EventForm(Form):

    name = TextField('Name', validators=[Required('A name is required')])
    title = TextField('Title', validators=[Required('A title is required')])
    from_date = DateField('From', description="Format: YYYY-MM-DD", validators=[Required('Propose a from date')])
    to_date = DateField('To', description="Format: YYYY-MM-DD", validators=[Required('Propose a to date')])
    venue = TextField('Venue', validators=[Required('Venue information is required')])


class ConfirmSignoutForm(Form):
    """
    Confirm a delete operation
    """
    # The labels on these widgets are not used. See delete.html.
    delete = SubmitField(u"Sign out")
    cancel = SubmitField(u"Cancel")


class ParticipantForm(Form):

    name = TextField('Name', validators=[Required('A name is required')])
    email = TextField('Email', validators=[Required('Please enter the email')])
    company = TextField('Company')
    job = TextField('Job Title')
    city = TextField('City')
    twitter = TextField('Twitter')
    tshirt_size = TextField('T-Shirt Size')
    nfc_id = HiddenField('NFC', validators=[Required('Please check the NFC Reader')])

def get_events():
    return Event.query.order_by('id').all()


class KioskForm(Form):

    name = TextField('Kiosk Name', validators=[Required('A name is required')])
    company = TextField('Company Name', description="Optional. You may want to leave this attribute empty if the name of the company is clear from the logo.")
    company_tag = TextField('Company Tagline', description="Optional")
    company_logo = TextField('Company Logo', description="Provide the URL for the image of the sponsor's logo.", validators=[Required('The logo is required'), URL(message="Please provide a valid URL")])
    tap_msg = TextField('Tapping message', description='Optional. Please tap your badge to ____? Leave blank to use default message.')
    event = QuerySelectField('Select an event', query_factory= get_events, get_label='title', allow_blank=False)
