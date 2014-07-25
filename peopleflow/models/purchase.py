
from . import db, BaseMixin
from .event import Event
from .ticket import Ticket
from .product import Product
from .participant import Participant
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class Purchase(db.Model, BaseMixin):

    __tablename__ = 'purchase'

    #: Participant who purchased an item
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=True)
    participant = db.relationship(Participant, primaryjoin=participant_id == Participant.id, backref=db.backref('purchase_list', cascade="all"))

    #: Product purchased
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product = db.relationship(Product, primaryjoin=product_id == Product.id)

    #: Ticket purchased. Only one of this or product must be set
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=True)
    ticket = db.relationship(Ticket, primaryjoin=ticket_id == Ticket.id)

    @property
    def item(self):
        return self.ticket or self.product

    @property
    def ticket_item(self):
        return self.ticket or self.product.ticket

    @property
    def type(self):
        if self.ticket or (self.product and self.product.ticket):
            return 'ticket'
        elif self.product:
            return 'product'