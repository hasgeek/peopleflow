# -*- coding: utf-8 -*-

from . import nav
from .. import app
from .. import lastuser
from ..models import db, Venue, Event
from ..forms import VenueForm
from coaster.views import load_model, load_models
from flask import flash, url_for, render_template
from baseframe.forms import render_redirect

@app.route('/event/<id>/venue/new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id':'id'}, 'event')
@nav.init(
    parent='event_venues',
    title="New Venue",
    urlvars=lambda objects: {'id':objects['event'].id},
    objects = ['event']
    )
def venue_new(event):
    form = VenueForm()
    if form.validate_on_submit():
        venue = Venue(event=event)
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash("Venue added")
        return render_redirect(url_for('event_venues', event=event.id))
    return render_template('form.html', form=form, title=u"New Venue — " + event.title, submit=u"Add", cancel_url=url_for('event_venues', event=event.id))


@app.route('/event/<event>/venues', methods=['GET'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Event, {'id':'event'}, 'event')
    )
@nav.init(
    parent='event',
    title="Venues",
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id}
    )
def event_venues(event):
    return render_template('event_venues.html', event=event)
