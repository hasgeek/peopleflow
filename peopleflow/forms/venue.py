# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form

class VenueForm(Form):
    title = wtforms.TextField('Venue Name', validators=[wtforms.validators.Required('A name is required')])