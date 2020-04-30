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

    from time_tracker_api.api import init_app
    init_app(app)

    if app.config.get('DEBUG'):
        app.logger.setLevel(logging.INFO)
        add_debug_toolbar(app)

    add_werkzeug_proxy_fix(app)

    cors_origins = app.config.get('CORS_ORIGINS')
    if cors_origins:
        enable_cors(app, cors_origins)


def add_debug_toolbar(app: Flask):
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


def enable_cors(app: Flask, cors_origins: str):
    from flask_cors import CORS
    cors_origins_list = cors_origins.split(",")
    CORS(app, resources={r"/*": {"origins": cors_origins_list}})
    app.logger.info("Set CORS access to [%s]" % cors_origins)


def add_werkzeug_proxy_fix(app: Flask):
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.logger.info("Add ProxyFix to serve swagger.json over https.")
