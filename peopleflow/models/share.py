
from peopleflow.models import db, BaseMixin
from peopleflow.models.participant import Participant
from peopleflow.models.kiosk import Kiosk
from datetime import datetime


class Share(db.Model, BaseMixin):
	kiosk_id = db.Column(db.Integer, db.ForeignKey('kiosk.id'), primary_key=True)
	participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), primary_key=True)
	share_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)