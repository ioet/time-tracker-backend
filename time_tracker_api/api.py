from flask_restplus import Api, fields

api = Api(version='1.0.1', title="TimeTracker API",
          description="API for the TimeTracker project")

# Common models structure
audit_fields = {
    'created_at': fields.Date(
        readOnly=True,
        title='Created',
        description='Date of creation'
    ),
    'tenant_id': fields.String(
        readOnly=True,
        title='Tenant',
        max_length=64,
        description='The tenant this belongs to',
    ),
    'created_by': fields.String(
        readOnly=True,
        title='Creator',
        max_length=64,
        description='User that created it',
    ),
}

# APIs
from time_tracker_api.projects import projects_api
api.add_namespace(projects_api.ns)

from time_tracker_api.activities import activities_api
api.add_namespace(activities_api.ns)

from time_tracker_api.technologies import technologies_api
api.add_namespace(technologies_api.ns)

from time_tracker_api.time_entries import time_entry_api
api.add_namespace(time_entry_api.ns)
