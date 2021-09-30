from flask import Flask
from flask_restplus import Resource, Api
from . import activities_endpoints

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='Time Tracker API',
    description='API for the TimeTracker project',
)

ns_activities = api.namespace('activities', description='Endpoint for activities')
ns_activities.route('/')(activities_endpoints.Activities)
ns_activities.route('/<string:activity_id>')(activities_endpoints.Activity)
