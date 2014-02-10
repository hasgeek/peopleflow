# -*- coding: utf-8 -*-

import wtforms
from baseframe.forms import Form
from ..models import Activity

class ActivityEditForm(Form):
    title = wtforms.TextField('Activity Name', validators=[wtforms.validators.Required('A name is required')])

class ActivityForm(ActivityEditForm):
    def __init__(self, venue, **kwargs):
        super(ActivityForm, self).__init__()
        self.venue = venue
    date = wtforms.DateField('Date', description="Format: YYYY-MM-DD", validators=[wtforms.validators.Required('The date is required')])

    def validate_date(self, field):
        exists = Activity.query.filter_by(venue=self.venue, date=field.data).first()
        if exists:
            raise wtforms.ValidationError(u'You cannot have two activities on the same date. %s already exists.' % exists.title)
        if field.data < self.venue.event.from_date or field.data > self.venue.event.to_date:
            raise wtforms.ValidationError(u'Activity date should be within the event dates %s & %s.' % (self.venue.event.from_date, self.venue.event.to_date))