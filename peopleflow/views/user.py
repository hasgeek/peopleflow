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


@app.route('/<year>/<eventname>/connect', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'name':'eventname'}, 'event')
def connect(event):
    if request.method=='GET':
        return render_template('connect.html', event = event)

    if request.method == 'POST':
        participants = []
        ids = request.form['id']
        ids = set(ids.split(','))
        msg = Message("Hello from "+event.title)
        for id in ids:
            participant = Participant.query.filter_by(event_id=event.id, nfc_id=id).first()
            participants.append(participant)

        for participant in participants:
            exchange = []
            for other in participants:
                if other!=participant:
                    exchange.append(other)
            msg.body= render_template('connectemail.md', name= participant.name, participants=exchange, event=event)
            msg.recipients=[participant.email]
            mail.send(msg)
        flash("Email sent!", "success")
        return render_template('connect.html', event = event)


@app.route('/print_card', methods=['POST'])
def print_card():
    twitter_handle = request.form['twitter']
    name = request.form['name']
    try:
        printlabel(line1=name, line2=twitter_handle)
        return jsonify({'msg': 'success'})
    except:
        return jsonify({'msg': 'failed'})
