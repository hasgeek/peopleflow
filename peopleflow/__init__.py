#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Website server for peopleflow
"""

from __future__ import absolute_import
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.lastuser import Lastuser
from flask.ext.lastuser.sqlalchemy import UserManager
from flask.ext.mail import Mail
from baseframe import baseframe, assets, Version
import coaster.app
from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

assets['peopleflow.css'][version] = 'css/app.css'

from . import models
from .models import db

def init_for(env):
    coaster.app.init_app(app, env)
    baseframe.init_app(app, requires=['baseframe', 'peopleflow'])
    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(db, models.User))