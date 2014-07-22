# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form
from coaster.utils import nullint

class ProductForm(Form):
    title = wtforms.TextField('Product Name', validators=[wtforms.validators.Required('A name is required')])
    ticket_id = wtforms.fields.SelectField('Ticket', description=u'If this this a ticket, which one is it?', coerce=nullint, choices=[], default='')
