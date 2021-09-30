from flask import Flask
from flask_restplus import Api

api = Api(
    version="0.1",
    title="TimeTracker API",
    description="API for the TimeTracker project",
    security="TimeTracker JWT",
)

def init_app(app: Flask):
    api.init_app(app)
    from V2.source.entry_points.flask_api import activities_namespace
    api.add_namespace(activities_namespace.app)