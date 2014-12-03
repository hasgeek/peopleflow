
from . import db, BaseMixin, BaseScopedNameMixin
from .event import Event
from sqlalchemy.ext.hybrid import hybrid_property

class Venue(BaseScopedNameMixin, db.Model):

    __tablename__ = 'venue'
    #: Venue Name
    title = db.Column(db.Unicode(80), nullable=False)

    #: Venue is for this event
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship(Event, foreign_keys=[event_id], backref=db.backref('venues'))
    parent = db.synonym('event')

    #: Whether this was fetched from Funnel
    from_funnel = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (db.UniqueConstraint('event_id', 'name'),)

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
