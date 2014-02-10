# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form

class VenueForm(Form):
    title = wtforms.TextField('Venue Name', description="Please be careful with the name. It is not changeable.", validators=[wtforms.validators.Required('A name is required')])