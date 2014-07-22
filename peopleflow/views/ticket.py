# -*- coding: utf-8 -*-

from . import nav
from .. import app
from .. import lastuser
from ..models import db, Ticket, Event
from ..forms import TicketForm
from coaster.views import load_model, load_models
from flask import flash, request, url_for, render_template
from baseframe.forms import render_redirect, ConfirmDeleteForm

@app.route('/event/<id>/ticket/new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id':'id'}, 'event')
@nav.init(
    parent='event_tickets',
    title="New Ticket",
    urlvars=lambda objects: {'id':objects['event'].id},
    objects = ['event']
    )
def ticket_new(event):
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(event=event)
        form.populate_obj(ticket)
        if not ticket.name:
            ticket.make_name()
        db.session.add(ticket)
        db.session.commit()
        flash("Ticket added")
        return render_redirect(url_for('event_tickets', event=event.id))
    return render_template('form.html', form=form, cancel_url=url_for('event_tickets', event=event.id))


@app.route('/event/<event>/tickets', methods=['GET'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Event, {'id':'event'}, 'event')
    )
@nav.init(
    parent='event',
    title="Tickets",
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id}
    )
def event_tickets(event):
    return render_template('event_tickets.html', event=event)

@app.route('/event/<event>/ticket/<ticket>/edit', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Ticket, {'id': 'ticket', 'event_id': 'event'}, 'ticket'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='event_tickets',
    title=lambda objects: "Edit: %s" % objects['ticket'].title,
    urlvars=lambda objects: {'event': objects['event'].id, 'ticket': objects['ticket'].id},
    objects = ['event']
    )
def ticket_edit(event, ticket):
    form = TicketForm(obj=ticket)
    if form.validate_on_submit():
        form.populate_obj(ticket)
        db.session.commit()
        flash("Ticket updated")
        return render_redirect(url_for('event_tickets', event=event.id))
    return render_template('form.html', form=form, cancel_url=url_for('event_tickets', event=event.id))

@app.route('/event/<event>/ticket/<ticket>/delete', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Ticket, {'id': 'ticket', 'event_id': 'event'}, 'ticket'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='event_tickets',
    title=lambda objects: "Confirm Delete: %s" % objects['ticket'].title,
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id, 'ticket': objects['ticket'].id}
    )
def ticket_delete(event, ticket):
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            for activity in ticket.activity:
                db.session.delete(activity)
            db.session.delete(ticket)
            flash("Deleted ticket %s" % ticket.title)
            db.session.commit()
        return render_redirect(url_for('event_tickets', event=event.id), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Delete '%s' ?" % (ticket.title),
        message=u"Do you really want to delete the ticket '%s'? All purchases attached to it will be deleted." % (ticket.title))
