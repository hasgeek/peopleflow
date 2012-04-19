
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
  
    __tablename__ = 'participant'
    
    #: Ticket number
    ticket_number = db.Column(db.Integer, nullable=True, unique=True)
    #: Name of the participant
    name = db.Column(db.Unicode(80), nullable=False)
    #: Email of the participant
    email = db.Column(db.Unicode(80), nullable=False)
    #: Ticket type
    ticket_type = db.Column(db.Unicode(80), default=u"Regular", nullable=True)
    #: Company name
    company = db.Column(db.Unicode(80), nullable=True)
    #: Job title
    job = db.Column(db.Unicode(80), nullable=True)
    #: City
    city = db.Column(db.Unicode(80), nullable=True)
    #: Twitter handle
    twitter = db.Column(db.Unicode(80), nullable=True)
    #: T-shirt size
    tshirt_size = db.Column(db.Integer, nullable=False, default=0)
    #: Date of registration
    regdate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    #:NFC ID
    nfc_id = db.Column(db.Unicode(80), unique=True)
    #: Order ID
    order_id = db.Column(db.Integer, nullable=True)
    #: Did the participant attend the event?
    attended = db.Column(db.Boolean, default=False, nullable=False)
    #: Datetime the participant showed up
    attend_date = db.Column(db.DateTime, nullable=True)
    #: Event the participant is attending
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


    def __repr__(self):
        return self.name
