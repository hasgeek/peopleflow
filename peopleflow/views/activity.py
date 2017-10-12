# -*- coding: utf-8 -*-

from . import nav
from .. import app
from .. import lastuser
from ..models import db, Venue, Event, Activity
from ..forms import ActivityForm, ActivityEditForm
from coaster.views import load_model, load_models
from flask import flash, url_for, render_template, request
from baseframe.forms import render_redirect, ConfirmDeleteForm

@app.route('/event/<event>/venue/<venue>/activity/new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Venue, {'event_id': 'event', 'id': 'venue'}, 'venue'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='venue_activity',
    title="New Activity",
    urlvars=lambda objects: {'event': objects['event'].id, 'venue': objects['venue'].id},
    objects = ['event', 'venue']
    )
def activity_new(event, venue):
    form = ActivityForm(venue)
    if form.validate_on_submit():
        activity = Activity(venue=venue)
        form.populate_obj(activity)
        db.session.add(activity)
        db.session.commit()
        flash("Activity added")
        return render_redirect(url_for('venue_activity', event=event.id, venue=venue.id))
    return render_template('form.html.jinja2', form=form, title=u"New Activity — %s - %s" % (venue.title, event.title), submit=u"Add", cancel_url=url_for('venue_activity', event=event.id, venue=venue.id))


@app.route('/event/<event>/venue/<venue>/activity', methods=['GET'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Venue, {'event_id': 'event', 'id': 'venue'}, 'venue'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='event_venues',
    title=lambda objects: "Activity: %s" % objects['venue'].title,
    objects=['event', 'venue'],
    urlvars=lambda objects: {'event': objects['event'].id, 'venue': objects['venue'].id}
    )
def venue_activity(event, venue):
    return render_template('venue_activity.html.jinja2', event=event, venue=venue)


@app.route('/event/<event>/venue/<venue>/activity/<activity>/edit', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Activity, {'venue_id': 'venue', 'id': 'activity'}, 'activity'),
    (Venue, {'event_id': 'event', 'id': 'venue'}, 'venue'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='venue_activity',
    title=lambda objects: "Edit: %s" % objects['activity'].title,
    urlvars=lambda objects: {'event': objects['event'].id, 'venue': objects['venue'].id, 'activity': objects['activity'].id},
    objects = ['event', 'venue', 'activity']
    )
def activity_edit(event, venue, activity):
    form = ActivityEditForm(obj=activity)
    if form.validate_on_submit():
        form.populate_obj(activity)
        db.session.commit()
        flash("Activity updated")
        return render_redirect(url_for('venue_activity', event=event.id, venue=venue.id))
    return render_template('form.html.jinja2', form=form, title=u"Edit Activity: %s — %s - %s" % (activity.title, venue.title, event.title), submit=u"Update", cancel_url=url_for('venue_activity', event=event.id, venue=venue.id))

@app.route('/event/<event>/venue/<venue>/activity/<activity>/delete', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Activity, {'venue_id': 'venue', 'id': 'activity'}, 'activity'),
    (Venue, {'id': 'venue', 'event_id': 'event'}, 'venue'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='venue_activity',
    title=lambda objects: "Confirm Delete: %s" % objects['activity'].title,
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id, 'venue': objects['venue'].id, 'activity': objects['activity'].id}
    )
def activity_delete(event, venue, activity):
    if activity.from_funnel:
        flash("You cannot delete activities created by Funnel", "danger")
        return render_redirect(url_for('event_venues', event=event.id))
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            db.session.delete(activity)
            flash("Deleted activity %s" % activity.title)
            db.session.commit()
        return render_redirect(url_for('venue_activity', event=event.id, venue=venue.id), code=303)
    return render_template('baseframe/delete.html.jinja2', form=form, title=u"Delete '%s' ?" % (activity.title),
        message=u"Do you really want to delete the activity '%s'? All checkins related to it will be deleted." % (activity.title))
