
from flask_restplus import Api

api = Api(version='1.0.1', title="TimeTracker API",
          description="API for the TimeTracker project")

# APIs
from time_tracker_api.projects import projects_endpoints
api.add_namespace(projects_endpoints.ns)