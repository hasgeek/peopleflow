
from . import db, BaseMixin
from .event import Event
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class Venue(db.Model, BaseMixin):

    __tablename__ = 'venue'
    #: Venue Name
    title = db.Column(db.Unicode(80), nullable=False)

    #: Venue is for this event
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship(Event, primaryjoin=event_id == Event.id, backref=db.backref('venues'))

    @hybrid_property
    def activity_dates(self):
        dates = [activity.date for activity in self.activity]
        dates.sort()
        return dates
    
    @hybrid_property
    def from_date(self):
        if not len(self.activity_dates):
            return None
        return self.activity_dates[0]

    @hybrid_property
    def to_date(self):
        if not len(self.activity_dates):
            return None
        return self.activity_dates[len(self.activity_dates) - 1]
