from flask import Flask


def create_app():
    flask_app = Flask(__name__)

    init_app(flask_app)

    return flask_app


def init_app(app):
    from .api import api
    api.init_app(app)