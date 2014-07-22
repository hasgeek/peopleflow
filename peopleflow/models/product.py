
from . import db, BaseScopedNameMixin
from .event import Event
from .ticket import Ticket
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class Product(db.Model, BaseScopedNameMixin):

    __tablename__ = 'product'
    #: Product Title
    title = db.Column(db.Unicode(120), nullable=False)

    __table_args__ = (db.UniqueConstraint("event_id", "name"), {})

    #: Product is for this event
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship(Event, primaryjoin=event_id == Event.id, backref=db.backref('products'))

    parent = db.synonym('event')

    #: If a product is a ticket, mapping with the ticket
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=True)
    ticket = db.relationship(Ticket, primaryjoin=ticket_id == Ticket.id)

    #: Source of purchase item
    source = db.Column(db.Unicode(30), default=None)
    id_source = db.Column(db.Unicode(30), default=None)