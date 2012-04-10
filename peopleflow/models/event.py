
from peopleflow.models import db, BaseMixin
from datetime import date

class Event(db.Model, BaseMixin):
    """
    Events
    """
    __tablename__ = 'events'
    #: Name of the event
    name = db.Column(db.Unicode(80), nullable=False)
    #: Title of the event
    title = db.Column(db.Unicode(80), nullable=False)
    #: Year of the event
    year = db.Column(db.Integer, default=date.today().year, nullable=False)
    #: Date of the event
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return self.name