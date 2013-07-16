from . import db, TimestampMixin, IdMixin


class CXLog(db.Model, IdMixin, TimestampMixin):
    """
    Contact Exchange Logs
    """
    __tablename__ = 'cxlog'
    #: List of users
    users = db.Column(db.Unicode(200), nullable=False)
    #: Mail Sent status
    sent = db.Column(db.Boolean, nullable=False)
    #: Log Message
    log_message = db.Column(db.Unicode, nullable=True)
