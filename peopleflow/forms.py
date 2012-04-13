#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from flaskext.wtf import (
    Form,
    TextField,
    Required,
    DateField,
    )


class EventForm(Form):

    name = TextField('Name', validators=[Required('A name is required')])
    title = TextField('Title', validators=[Required('A title is required')])
    date = DateField('Date', validators=[Required('Propose a date')])
    venue = TextField('Venue', validators=[Required('Venue information is required')])