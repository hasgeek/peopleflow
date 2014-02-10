# -*- coding: utf-8 -*-

from . import nav
from .. import app
from .. import lastuser
from ..models import db, Venue, Event
from ..forms import VenueForm
from coaster.views import load_model, load_models
from flask import flash, request, url_for, render_template
from baseframe.forms import render_redirect, ConfirmDeleteForm

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
        if not venue.name:
            venue.make_name()
        db.session.add(venue)
        db.session.commit()
        flash("Venue added")
        return render_redirect(url_for('event_venues', event=event.id))
    return render_template('form.html', form=form, cancel_url=url_for('event_venues', event=event.id))


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

@app.route('/event/<event>/venue/<venue>/edit', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Venue, {'id': 'venue', 'event_id': 'event'}, 'venue'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='event_venues',
    title=lambda objects: "Edit: %s" % objects['venue'].title,
    urlvars=lambda objects: {'event': objects['event'].id, 'venue': objects['venue'].id},
    objects = ['event']
    )
def venue_edit(event, venue):
    form = VenueForm(obj=venue)
    if form.validate_on_submit():
        form.populate_obj(venue)
        db.session.commit()
        flash("Venue updated")
        return render_redirect(url_for('event_venues', event=event.id))
    return render_template('form.html', form=form, cancel_url=url_for('event_venues', event=event.id))

@app.route('/event/<event>/venue/<venue>/delete', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Venue, {'id': 'venue', 'event_id': 'event'}, 'venue'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='event_venues',
    title=lambda objects: "Confirm Delete: %s" % objects['venue'].title,
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id, 'venue': objects['venue'].id}
    )
def venue_delete(event, venue):
    if venue.from_funnel:
        flash("You cannot delete venues created by Funnel", "danger")
        return render_redirect(url_for('event_venues', event=event.id))
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            for activity in venue.activity:
                db.session.delete(activity)
            db.session.delete(venue)
            flash("Deleted venue %s" % venue.title)
            db.session.commit()
        return render_redirect(url_for('event_venues', event=event.id), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Delete '%s' ?" % (venue.title),
        message=u"Do you really want to delete the venue '%s'? All it's activity items and checkins will also get deleted." % (event.title))
