# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form
from coaster.utils import nullint

class ProductForm(Form):
    title = wtforms.TextField('Product Name', validators=[wtforms.validators.Required('A name is required')])
    ticket_id = wtforms.fields.SelectField('Ticket', description=u'If this this a ticket, which one is it?', coerce=nullint, choices=[], default='')

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(ProductForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if obj and obj.source:
            del self.title
