from flask import Flask
from flask_restplus import Api


def create_app():
    flask_app = Flask(__name__)
    app = Api(app=flask_app)

    from time_tracker_api.projects.projects_endpoints import ns as projects_ns
    app.add_namespace(projects_ns)

    return flask_app
