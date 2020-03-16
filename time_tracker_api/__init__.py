import os

from flask import Flask


def create_app(config_path='time_tracker_api.config.DefaultConfig',
               config_data=None):
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
    from .database import init_app as init_database
    init_database(app)

    from .api import api
    api.init_app(app)
