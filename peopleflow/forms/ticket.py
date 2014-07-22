# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form

class TicketForm(Form):
    title = wtforms.TextField('Ticket Name', validators=[wtforms.validators.Required('A name is required')])
