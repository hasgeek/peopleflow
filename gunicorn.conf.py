#!/usr/bin/env python
# -*- coding: utf-8 -*-

bind = '0.0.0.0:8000'
workers = 10
proc_name = 'peopleflow'
error = "/tmp/peopleflow_error.log"
worker_class = "gevent"
debug = True
daemon = True
pidfile = "/tmp/peopleflow.pid"
logfile = "/tmp/peopleflow.log"
loglevel= "debug"