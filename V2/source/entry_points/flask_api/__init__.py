from flask import Flask
from flask_restplus import Namespace, Resource, Api
from http import HTTPStatus
from . import activities_endpoints


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    api = Api(
        app,
        version='1.0',
        title='Time Tracker API',
        description='API for the TimeTracker project',
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    ns_activities = Namespace('activities', description='Endpoint for activities')
    ns_activities.route('/')(activities_endpoints.Activities)
    ns_activities.route('/<string:activity_id>')(activities_endpoints.Activity)

    api.add_namespace(ns_activities)

    return app
