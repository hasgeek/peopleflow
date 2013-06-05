from flask.ext.sqlalchemy import SQLAlchemy
from .. import app
from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin

db = SQLAlchemy(app)

from .participant import *
from .event import *
from .user import *
from .kiosk import *