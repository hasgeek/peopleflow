#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from flaskext.wtf import (
    Form,
    TextField,
    Required,
    DateField,
    SubmitField,
    HiddenField,
    )


class EventForm(Form):

    name = TextField('Name', validators=[Required('A name is required')])
    title = TextField('Title', validators=[Required('A title is required')])
    date = DateField('Date', validators=[Required('Propose a date')])
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
    # regdate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # nfc_id = db.Column(db.Unicode(80), unique=True)
    # attended = db.Column(db.Boolean, default=False, nullable=False)
    #: Datetime the participant showed up
    # attend_date = db.Column(db.DateTime, nullable=True)
    #: Event the participant is attending
    # event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

