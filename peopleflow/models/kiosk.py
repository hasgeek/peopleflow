
from peopleflow.models import db, BaseMixin
from peopleflow.models.event import Event
from datetime import datetime

kiosk_participants = db.Table('kiosk_participants',
db.Column('kiosk_id', db.Integer, db.ForeignKey('kiosk.id')),
db.Column('participant_id', db.Integer, db.ForeignKey('participant.id')),
db.Column('share_date', db.DateTime, default=datetime.utcnow, nullable=False))

class Kiosk(db.Model, BaseMixin):

	__tablename__ = 'kiosk'
	#: Name of the Kiosk

	name = db.Column(db.Unicode(80), nullable=False)

	#: Name of the Sponsor
	company = db.Column(db.Unicode(80), nullable=True)
	#: Event at which the kiosk is present. kiosk.event gives access.
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
	event = db.relationship(Event, primaryjoin=event_id == Event.id)


	#: List of participants who showed up at the Kiosk. kiosk.participants gives access to the objects.
	participants = db.relationship('Participant', secondary=kiosk_participants,
	backref=db.backref('kiosk', lazy='dynamic'))