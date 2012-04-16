from flaskext.sqlalchemy import SQLAlchemy
from peopleflow import app
from coaster.sqlalchemy import BaseMixin, BaseNameMixin

db = SQLAlchemy(app)

from peopleflow.models.participant import *
from peopleflow.models.event import *
from peopleflow.models.user import *