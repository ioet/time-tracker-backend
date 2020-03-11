
from flask_restplus import Api

api = Api(version='1.0.1', title="TimeTracker API",
          description="API for the TimeTracker project")

# APIs
from time_tracker_api.projects import projects_api
api.add_namespace(projects_api.ns)

from time_tracker_api.activities import activities_api
api.add_namespace(activities_api.ns)

from time_tracker_api.time_entries import time_entry_api
api.add_namespace(time_entry_api.ns)
