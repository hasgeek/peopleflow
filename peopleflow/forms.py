#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from flaskext.wtf import (
    Form,
    TextField,
    Required,
    DateField,
    SubmitField,
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