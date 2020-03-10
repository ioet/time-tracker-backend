#!/usr/bin/env python3
"""
This file is needed by gunicorn to run
"""
from time_tracker_api import create_app

app = create_app()
print("BPM Projects API server was created")