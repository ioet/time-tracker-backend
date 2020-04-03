import pyodbc

import sqlalchemy
from faker import Faker
from flask import current_app as app
from flask_restplus import Api, fields
from flask_restplus._http import HTTPStatus

faker = Faker()

api = Api(version='1.0.1',
          title="TimeTracker API",
          description="API for the TimeTracker project")

# Common models structure
audit_fields = {
    'deleted': fields.String(
        readOnly=True,
        required=True,
        title='Last event Identifier',
        description='Last event over this resource',
        example=faker.uuid4(),
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
        return {'message': 'It already exists or references data that does not exist.'}, HTTPStatus.CONFLICT
    else:
        return {'message': 'Data integrity issues.'}, HTTPStatus.CONFLICT


@api.errorhandler(sqlalchemy.exc.DataError)
def handle_invalid_data_error(e):
    """Return a 422 because the user entered data of an invalid type"""
    return {'message': 'The processed data was invalid. Please correct it.'}, HTTPStatus.UNPROCESSABLE_ENTITY


@api.errorhandler(pyodbc.OperationalError)
def handle_connection_error(e):
    """Return a 500 due to a issue in the connection to a 3rd party service"""
    return {'message': 'Connection issues. Please try again in a few minutes.'}, HTTPStatus.SERVICE_UNAVAILABLE


@api.errorhandler
def generic_exception_handler(e):
    app.logger.error(e)
    return {'message': 'An unhandled exception occurred.'}, HTTPStatus.INTERNAL_SERVER_ERROR
