#!/usr/bin/env python
# -*- coding: utf-8 -*-
from peopleflow import app, mail
from flask import Flask, abort, request, render_template, redirect, url_for
from flask import flash, session, g, Response

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

