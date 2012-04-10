
from peopleflow.models import db, BaseMixin
from datetime import datetime


TSHIRT_SIZES = [
    ('',  u''),
    ('1', u'XS'),
    ('2', u'S'),
    ('3', u'M'),
    ('4', u'L'),
    ('5', u'XL'),
    ('6', u'XXL'),
    ('7', u'XXXL'),
    ]

class Participant(db.Model, BaseMixin):
  
    __tablename__ = 'participants'
    
    #: Ticket number
    ticket_number = db.Column(db.Integer, nullable=False)
    #: Name of the participant
    name = db.Column(db.Unicode(80), nullable=False)
    #: Email of the participant
    email = db.Column(db.Unicode(80), nullable=False)
    #: Ticket type
    ticket_type = db.Column(db.Unicode(80), default=u"Regular", nullable=False)
    #: Company name
    company = db.Column(db.Unicode(80), nullable=True)
    #: Job title
    job = db.Column(db.Unicode(80), nullable=True)
    #: City
    city = db.Column(db.Unicode(80), nullable=False)
    #: Twitter handle
    twitter = db.Column(db.Unicode(80), nullable=True)
    #: T-shirt size
    tshirtsize = db.Column(db.Integer, nullable=False, default=0)
    #: Date of registration
    regdate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    #: Order ID
    orderid = db.Column(db.Integer, nullable=False)
    #: Did the participant attend the event?
    attended = db.Column(db.Boolean, default=False, nullable=False)
    #: Datetime the participant showed up
    attenddate = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return self.name
