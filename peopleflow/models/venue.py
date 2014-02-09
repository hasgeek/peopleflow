
from . import db, BaseMixin
from .event import Event
from datetime import datetime

class Venue(db.Model, BaseMixin):

    __tablename__ = 'venue'
    #: Venue Name
    title = db.Column(db.Unicode(80), nullable=False)

    #: Sub Event From & To Dates
    from_date = db.Column(db.Date, nullable=True)
    to_date = db.Column(db.Date, nullable=True)

    #: Venue is for this event
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship(Event, primaryjoin=event_id == Event.id, backref=db.backref('venues'))
    