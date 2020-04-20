from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError, CosmosHttpResponseError
from faker import Faker
from flask import current_app as app
from flask_restplus import Api, fields
from flask_restplus._http import HTTPStatus

from commons.data_access_layer.cosmos_db import CustomError
from time_tracker_api.version import __version__

faker = Faker()

api = Api(
    version=__version__,
    title="TimeTracker API",
    description="API for the TimeTracker project"
)

# For matching UUIDs
UUID_REGEX = '[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}'

# Common models structure
common_fields = {
    'id': fields.String(
        title='Identifier',
        readOnly=True,
        required=True,
        description='The unique identifier',
        pattern=UUID_REGEX,
        example=faker.uuid4(),
    ),
    'tenant_id': fields.String(
        title='Identifier of Tenant',
        readOnly=True,
        required=True,
        description='Tenant it belongs to',
        # pattern=UUID_REGEX, This must be confirmed
        example=faker.uuid4(),
    ),
    'deleted': fields.String(
        readOnly=True,
        required=True,
        title='Last event Identifier',
        description='Last event over this resource',
        pattern=UUID_REGEX,
    ),
}

# APIs
from time_tracker_api.projects import projects_namespace

api.add_namespace(projects_namespace.ns)

from time_tracker_api.activities import activities_namespace

api.add_namespace(activities_namespace.ns)

from time_tracker_api.time_entries import time_entries_namespace

api.add_namespace(time_entries_namespace.ns)

from time_tracker_api.project_types import project_types_namespace

api.add_namespace(project_types_namespace.ns)

from time_tracker_api.customers import customers_namespace

api.add_namespace(customers_namespace.ns)

"""
Error handlers
"""


@api.errorhandler(CosmosResourceExistsError)
def handle_cosmos_resource_exists_error(error):
    return {'message': 'It already exists'}, HTTPStatus.CONFLICT


@api.errorhandler(CosmosResourceNotFoundError)
@api.errorhandler(StopIteration)
def handle_not_found_errors(error):
    return {'message': 'It was not found'}, HTTPStatus.NOT_FOUND


@api.errorhandler(CosmosHttpResponseError)
def handle_cosmos_http_response_error(error):
    return {'message': 'Invalid request. Please verify your data.'}, HTTPStatus.BAD_REQUEST


@api.errorhandler(AttributeError)
def handle_attribute_error(error):
    return {'message': "There are missing attributes"}, HTTPStatus.UNPROCESSABLE_ENTITY


@api.errorhandler(CustomError)
def handle_custom_error(error):
    return {'message': error.description}, error.code


@api.errorhandler
def default_error_handler(error):
    app.logger.error(error)
    return {'message': 'An unhandled exception occurred.'}, HTTPStatus.INTERNAL_SERVER_ERROR
