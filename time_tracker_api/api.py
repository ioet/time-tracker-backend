import pyodbc

import sqlalchemy
from faker import Faker
from flask import current_app as app
from flask_restplus import Api, fields

faker = Faker()

api = Api(version='1.0.1',
          title="TimeTracker API",
          description="API for the TimeTracker project")

# Common models structure
audit_fields = {
    'created_at': fields.Date(
        readOnly=True,
        title='Created',
        description='Date of creation',
        example=faker.iso8601(end_datetime=None),
    ),
    'updated_at': fields.Date(
        readOnly=True,
        title='Updated',
        description='Date of update',
        example=faker.iso8601(end_datetime=None),
    ),
    # TODO Activate it when the tenants model is implemented
    # 'tenant_id': fields.String(
    #     readOnly=True,
    #     title='Tenant',
    #     max_length=64,
    #     description='The tenant this belongs to',
    #     example=faker.random_int(1, 9999),
    # ),
    'created_by': fields.String(
        readOnly=True,
        title='Creator',
        max_length=64,
        description='User that created it',
        example='anonymous',
    ),
    'updated_by': fields.String(
        readOnly=True,
        title='Updater',
        max_length=64,
        description='User that updated it',
        example='anonymous',
    ),
}

# APIs
from time_tracker_api.projects import projects_namespace

api.add_namespace(projects_namespace.ns)

from time_tracker_api.activities import activities_namespace

api.add_namespace(activities_namespace.ns)

from time_tracker_api.time_entries import time_entries_namespace

api.add_namespace(time_entries_namespace.ns)

"""
Error handlers
"""


@api.errorhandler(sqlalchemy.exc.IntegrityError)
def handle_db_integrity_error(e):
    """Handles errors related to data consistency"""
    if e.code == 'gkpj':
        return {'message': 'It already exists.'}, 409
    else:
        return {'message': 'Data integrity issues.'}, 409


@api.errorhandler(sqlalchemy.exc.DataError)
def handle_invalid_data_error(e):
    """Return a 422 because the user entered data of an invalid type"""
    return {'message': 'The processed data was invalid. Please correct it.'}, 422


@api.errorhandler(pyodbc.OperationalError)
def handle_connection_error(e):
    """Return a 500 due to a issue in the connection to a 3rd party service"""
    return {'message': 'Connection issues. Please try again in a few minutes.'}, 500


@api.errorhandler
def generic_exception_handler(e):
    app.logger.error(e)
    return {'message': 'An unhandled exception occurred.'}, 500
