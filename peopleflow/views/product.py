# -*- coding: utf-8 -*-

from . import nav
from .. import app
from .. import lastuser
from ..models import db, Product, Event
from ..forms import ProductForm
from coaster.views import load_model, load_models
from flask import flash, request, url_for, render_template
from baseframe.forms import render_redirect, ConfirmDeleteForm

@app.route('/event/<id>/product/new', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_model(Event, {'id':'id'}, 'event')
@nav.init(
    parent='event_products',
    title="New Product",
    urlvars=lambda objects: {'id':objects['event'].id},
    objects = ['event']
    )
def product_new(event):
    form = ProductForm()
    form.ticket_id.choices = [('', '')] + [(ticket.id, ticket.title) for ticket in event.tickets]
    if form.validate_on_submit():
        product = Product(event=event)
        form.populate_obj(product)
        if not product.name:
            product.make_name()
        db.session.add(product)
        db.session.commit()
        flash("Product added")
        return render_redirect(url_for('event_products', event=event.id))
    return render_template('form.html', form=form, cancel_url=url_for('event_products', event=event.id))


@app.route('/event/<event>/products', methods=['GET'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Event, {'id':'event'}, 'event')
    )
@nav.init(
    parent='event',
    title="Products",
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id}
    )
def event_products(event):
    return render_template('event_products.html', event=event)

@app.route('/event/<event>/product/<product>/edit', methods=['GET', 'POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Product, {'id': 'product', 'event_id': 'event'}, 'product'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='event_products',
    title=lambda objects: "Edit: %s" % objects['product'].title,
    urlvars=lambda objects: {'event': objects['event'].id, 'product': objects['product'].id},
    objects = ['event']
    )
def product_edit(event, product):
    form = ProductForm(obj=product)
    form.ticket_id.choices = [('', '')] + [(ticket.id, ticket.title) for ticket in event.tickets]
    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        flash("Product updated")
        return render_redirect(url_for('event_products', event=event.id))
    return render_template('form.html', form=form, cancel_url=url_for('event_products', event=event.id))

@app.route('/event/<event>/product/<product>/delete', methods=['GET','POST'])
@lastuser.requires_permission('siteadmin')
@load_models(
    (Product, {'id': 'product', 'event_id': 'event'}, 'product'),
    (Event, {'id': 'event'}, 'event'))
@nav.init(
    parent='event_products',
    title=lambda objects: "Confirm Delete: %s" % objects['product'].title,
    objects=['event'],
    urlvars=lambda objects: {'event': objects['event'].id, 'product': objects['product'].id}
    )
def product_delete(event, product):
    if product.source:
        flash("You cannot delete products not created by Peopleflow", "danger")
        return render_redirect(url_for('event_products', event=event.id))
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            for activity in product.activity:
                db.session.delete(activity)
            db.session.delete(product)
            flash("Deleted product %s" % product.title)
            db.session.commit()
        return render_redirect(url_for('event_products', event=event.id), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Delete '%s' ?" % (product.title),
        message=u"Do you really want to delete the product '%s'? All purchases attached to it will be deleted." % (product.title))
