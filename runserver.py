#!/usr/bin/env python
import sys
from peopleflow import app

try:
    port = int(sys.argv[1])
except (IndexError, ValueError):
    port = 8000

app.run('0.0.0.0', port, debug=True)
