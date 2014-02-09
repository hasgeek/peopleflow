
from . import db, BaseMixin
from .venue import Venue
from datetime import datetime

class Activity(db.Model, BaseMixin):

    __tablename__ = 'activity'

    #: Activity Name
    title = db.Column(db.Unicode(80), nullable=False)

    #Activity Date
    date = db.Column(db.Date, nullable=False)

    #: Venue at which the activity is happening.
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    venue = db.relationship(Venue, primaryjoin=venue_id == Venue.id, backref=db.backref('activity'))