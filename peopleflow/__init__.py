#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Website server for peopleflow
"""

from flask import Flask
from flaskext.assets import Environment, Bundle
from flaskext.mail import Mail
from baseframe import baseframe, baseframe_js, baseframe_css
from coaster import configureapp
from os import environ

# First, make an app and config it

app = Flask(__name__, instance_relative_config=True)
configureapp(app, 'PEOPLEFLOW_ENV')
mail = Mail()
mail.init_app(app)
assets = Environment(app)

# Second, setup baseframe and assests

app.register_blueprint(baseframe)

css = Bundle(baseframe_css,
			 'css/app.css',
			 'css/jquery-ui.css')

js = Bundle('js/libs/jquery-1.6.4.js',
            'js/libs/jquery.form.js',
            'js/libs/jquery-ui-1.8.4.min.js',
            filters='jsmin', output='js/packed.js')

assets.register('js_all', js)
assets.register('css_all', css)


# Third, after config, import the models and views

import peopleflow.models
import peopleflow.views
# from peopleflow.views.login import lastuser
# if environ.get('PEOPLEFLOW_ENV') == 'prod':
#     import peopleflow.loghandler

# Fourth, setup admin for the models

# from flask.ext import admin
# from flask.ext.admin.datastore.sqlalchemy import SQLAlchemyDatastore
# from geekup.views.login import lastuser

# admin_datastore = SQLAlchemyDatastore(geekup.models, geekup.models.db.session)
# admin_blueprint = admin.create_admin_blueprint(admin_datastore,
#     view_decorator=lastuser.requires_permission('siteadmin'))

# app.register_blueprint(admin_blueprint, url_prefix='/admin')
