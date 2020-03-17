from flask_restplus import Api, fields
from faker import Faker

faker = Faker()

api = Api(version='1.0.1', title="TimeTracker API",
          description="API for the TimeTracker project")

# Common models structure
audit_fields = {
    'created_at': fields.Date(
        readOnly=True,
        title='Created',
        description='Date of creation',
        example=faker.iso8601(end_datetime=None),
    ),
    'tenant_id': fields.String(
        readOnly=True,
        title='Tenant',
        max_length=64,
        description='The tenant this belongs to',
        example=faker.random_int(1, 9999),
    ),
    'created_by': fields.String(
        readOnly=True,
        title='Creator',
        max_length=64,
        description='User that created it',
        example=faker.random_int(1, 9999),
    ),
}

# APIs
from time_tracker_api.projects import projects_namespace
api.add_namespace(projects_namespace.ns)

from time_tracker_api.activities import activities_namespace
api.add_namespace(activities_namespace.ns)

from time_tracker_api.technologies import technologies_namespace
api.add_namespace(technologies_namespace.ns)

from time_tracker_api.time_entries import time_entries_namespace
api.add_namespace(time_entries_namespace.ns)
