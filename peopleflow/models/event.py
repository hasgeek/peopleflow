# -*- coding: utf-8 -*-

from . import db, BaseMixin
from datetime import date
from coaster.sqlalchemy import JsonDict

class Event(db.Model, BaseMixin):
    """
    Events
    """
    __tablename__ = 'event'
    #: Name of the event
    name = db.Column(db.Unicode(80), nullable=False)
    #: Title of the event
    title = db.Column(db.Unicode(80), nullable=False)
    #: From Date of the event
    from_date = db.Column(db.Date, nullable=True)
    #: To Date of the event
    to_date = db.Column(db.Date, nullable=True)
    #: ID of the event on Doattend
    doattend_id = db.Column(db.Unicode(10), nullable=True)
    #: Funnel Proposal Space
    funnel_space = db.Column(db.Unicode(25), nullable=True)
    #:Venue
    venue = db.Column(db.Unicode(80), nullable=False)
    #: List of participants, event.participants gives access to
    #: the objects
    participants = db.relationship('Participant', backref='event',
                      lazy='dynamic')
    #: Print type: label, badge
    print_type = db.Column(db.Unicode(10), default=u'badge', nullable=False)
    #: If print type is badge, printing options for badges
    options = db.Column(JsonDict, nullable=False)
    
    #: List of kiosks. event.kiosks gives access to the objects.
    # kiosks = db.relationship('Kiosk', backref='event', lazy='dynamic')

    def __repr__(self):
        return self.name
