#!/usr/bin/env python
import sys
from peopleflow import app, init_for
init_for('dev')

try:
    port = int(sys.argv[1])
except (IndexError, ValueError):
    port = 8000

app.run('0.0.0.0', port, debug=True)