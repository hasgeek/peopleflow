
from . import db, BaseScopedNameMixin
from .event import Event
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class Ticket(db.Model, BaseScopedNameMixin):

    __tablename__ = 'ticket'
    #: Ticket Title
    title = db.Column(db.Unicode(120), nullable=False)

    __table_args__ = (db.UniqueConstraint("event_id", "name"), {})

    on_the_spot = db.Column(db.Boolean, default=False, nullable=False)

    #: Ticket is for this event
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship(Event, primaryjoin=event_id == Event.id, backref=db.backref('tickets'))

    parent = db.synonym('event')
    