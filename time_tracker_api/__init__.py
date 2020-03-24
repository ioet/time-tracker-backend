import logging
import os

from flask import Flask

flask_app: Flask = None


def create_app(config_path='time_tracker_api.config.DefaultConfig',
               config_data=None):
    global flask_app
    flask_app = Flask(__name__)

    init_app_config(flask_app, config_path, config_data)
    init_app(flask_app)

    return flask_app


def init_app_config(app: Flask, config_path: str, config_data: dict = None):
    if config_path:
        app.config.from_object(config_path)
    else:
        # ensure the instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # Located in `/instance`
        app.config.from_pyfile('config.py', silent=True)

    if config_data:
        app.config.update(config_data)


def init_app(app: Flask):
    from time_tracker_api.database import init_app as init_database
    init_database(app)

    from time_tracker_api.api import api
    api.init_app(app)

    if app.config.get('DEBUG'):
        app.logger.setLevel(logging.INFO)
        add_debug_toolbar(app)


def add_debug_toolbar(app):
    app.config['DEBUG_TB_PANELS'] = (
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel'
    )

    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)
