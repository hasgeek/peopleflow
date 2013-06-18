#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import app
from flask import Flask, abort, request, render_template, redirect, url_for, make_response, jsonify
from werkzeug import secure_filename
from flask import flash, session, g, Response
from coaster.views import load_model, load_models, jsonp
from ..forms import EventForm, ConfirmSignoutForm, ParticipantForm, KioskForm
from ..models import db, Event, Participant, Kiosk
from .. import lastuser
from dateutil import parser as dateparser
from pytz import utc, timezone
import os, csv, re
from StringIO import StringIO
from datetime import datetime
from baseframe.forms import render_form, render_redirect, ConfirmDeleteForm
import time
from flask.ext.mail import Message
from markdown import markdown
from ..helpers.printlabel import printlabel
import urllib
import hashlib


@app.route('/print_card', methods=['POST'])
def print_card():
    twitter_handle = request.form['twitter']
    name = request.form['name']
    try:
        printlabel(line1=name, line2=twitter_handle)
        return jsonify({'msg': 'success'})
    except:
        return jsonify({'msg': 'failed'})
