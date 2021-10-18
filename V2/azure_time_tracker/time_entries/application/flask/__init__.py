from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_restplus import Namespace, Resource, Api
from http import HTTPStatus
from .activities_endpoints import Activities, Activity
from . import activities_endpoints

csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__)
    csrf.init_app(app)

    api = Api(
        app,
        version='1.0',
        title='Time Tracker API',
        description='API for the TimeTracker project',
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    activities_namespace = Namespace(
        'activities', description='Endpoint for activities'
    )
    activities_namespace.route('/')(activities_endpoints.Activities)
    activities_namespace.route('/<string:activity_id>')(
        activities_endpoints.Activity
    )

    api.add_namespace(activities_namespace)

    return app
