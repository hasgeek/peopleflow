#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Website server for peopleflow
"""

from os import environ
from flask import Flask
from flask_assets import Environment, Bundle
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager
from flask_mail import Mail, Message
from baseframe import baseframe, assets, Version
import coaster.app
from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)
if app.config.get('GUNICORN_ENV'):
	init_for(app.config.get('GUNICORN_ENV'))
lastuser = Lastuser()

assets['peopleflow.css'][version] = 'css/app.css'
assets['peopleflow.js'][version] = 'js/app.js'
assets['cooldown.js'][version] = 'js/cooldown.js'
assets['indicators.css'][version] = 'css/indicators.css'
assets['indicators.js'][version] = 'js/indicators.js'

from . import models, views
from .models import db
from .views import nav

def init_for(env):
    coaster.app.init_app(app, env)
    db.init_app(app)
    db.app = app
    baseframe.init_app(app, requires=['baseframe', 'jquery.ui', 'toastr', 'indicators', 'peopleflow', 'cooldown'])
    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(db, models.User))
    nav.init_app(app)
