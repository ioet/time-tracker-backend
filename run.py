#!/usr/bin/env python3
"""
This file is needed by gunicorn to run
"""
from time_tracker_api import create_app

app = create_app('time_tracker_api.config.ProductionConfig')
print("TimeTracker API server created!")
