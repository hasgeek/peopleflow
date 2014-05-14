
from . import db, BaseMixin
from .venue import Venue
from datetime import datetime

activity_checkins = db.Table('activity_checkins',
db.Column('activity_id', db.Integer, db.ForeignKey('activity.id')),
db.Column('participant_id', db.Integer, db.ForeignKey('participant.id')),
db.Column('email', db.Boolean, default=False, nullable=False),
db.Column('time', db.DateTime, default=datetime.utcnow, nullable=False))

class Activity(db.Model, BaseMixin):

    __tablename__ = 'activity'

    #: Activity Name
    title = db.Column(db.Unicode(80), nullable=False)

    #Activity Date
    date = db.Column(db.Date, nullable=False)

    #: Whether this was fetched from Funnel
    from_funnel = db.Column(db.Boolean, default=False, nullable=False)

    #: Venue at which the activity is happening.
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    venue = db.relationship(Venue, primaryjoin=venue_id == Venue.id, backref=db.backref('activity'))

    attendees = db.relationship('Participant', secondary=activity_checkins,
    backref=db.backref('activity', lazy='dynamic'))

    def checkin(self, participant):
        if not self.checkedin(participant):
            self.attendees.append(participant)
            db.session.commit()

    def checkedin(self, participant):
        return participant in self.attendees
