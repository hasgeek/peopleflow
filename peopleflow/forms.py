#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from flaskext.wtf import (
    Form,
    TextField,
    SelectField,
    QuerySelectField,
    QuerySelectMultipleField,
    Required,
    Email,
    NoneOf,
    DateField,
    TextAreaField,
    )


class EventForm(Form):

    name = TextField('Name', validators=[Required('A name is required')])
    title = TextField('Title', validators=[Required('A title is required')])
    date = DateField('Date', validators=[Required('Propose a date')])