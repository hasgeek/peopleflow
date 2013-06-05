# -*- coding: utf-8 -*-

from . import db, BaseMixin
from datetime import date


class Event(db.Model, BaseMixin):
    """
    Events
    """
    __tablename__ = 'event'
    #: Name of the event
    name = db.Column(db.Unicode(80), nullable=False)
    #: Title of the event
    title = db.Column(db.Unicode(80), nullable=False)
    #: Year of the event
    year = db.Column(db.Integer, default=date.today().year, nullable=False)
    #: Date of the event
    date = db.Column(db.Date, nullable=False)
    #:Venue
    venue = db.Column(db.Unicode(80), nullable=False)
    #: List of participants, event.participants gives access to
    #: the objects
    participants = db.relationship('Participant', backref='event',
                      lazy='dynamic')
    #: List of kiosks. event.kiosks gives access to the objects.
    # kiosks = db.relationship('Kiosk', backref='event', lazy='dynamic')

    def __repr__(self):
        return self.name
