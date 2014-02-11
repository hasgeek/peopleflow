# -*- coding: utf-8 -*-

from . import db, BaseMixin
from datetime import date
from coaster.sqlalchemy import JsonDict
from sqlalchemy.ext.hybrid import hybrid_property

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
    #: List of participants, event.participants gives access to
    #: the objects
    participants = db.relationship('Participant', backref='event',
                      lazy='dynamic')
    #: Print type: label, badge
    print_type = db.Column(db.Unicode(10), default=u'badge', nullable=False)
    #: If print type is badge, printing options for badges
    options = db.Column(JsonDict, nullable=False)
    speaker_options = db.Column(JsonDict, nullable=False)
    crew_options = db.Column(JsonDict, nullable=False)
    
    #: List of kiosks. event.kiosks gives access to the objects.
    # kiosks = db.relationship('Kiosk', backref='event', lazy='dynamic')

    @hybrid_property
    def nfc(self):
        return 'nfc' in self.options and self.options['nfc']

    def activity(self, today=False):
        activity = []
        for venue in self.venues:
            for item in venue.activity:
                if not today or date.today() == item.date:
                    activity.append(item)
        return activity

    @hybrid_property
    def active(self):
        return bool(len(self.activity(today=True)))

    def __repr__(self):
        return self.name
