from azure.cosmos.exceptions import (
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
    CosmosHttpResponseError,
)
from faker import Faker
from flask import current_app as app, Flask
from flask_restplus import Api, fields, Model
from flask_restplus import namespace
from flask_restplus._http import HTTPStatus
from flask_restplus.reqparse import RequestParser

from commons.data_access_layer.cosmos_db import CustomError
from time_tracker_api import security
from time_tracker_api.security import UUID_REGEX
from time_tracker_api.version import __version__

faker = Faker()

api = Api(
    version=__version__,
    title="TimeTracker API",
    description="API for the TimeTracker project",
    authorizations=security.authorizations,
    security="TimeTracker JWT",
)


def remove_required_constraint(model: Model):
    result = model.resolved
    for attrib in result:
        result[attrib].required = False

    return result


def add_update_last_entry_if_overlap(time_entry_model: Model):
    time_entry_flag = {
        'update_last_entry_if_overlap': fields.Boolean(
            title='Update last entry if overlap',
            required=False,
            description='Flag that indicates if the last time entry is updated',
            example=True,
        )
    }
    new_model = time_entry_model.clone('TimeEntryInput', time_entry_flag)
    return new_model


def create_attributes_filter(
    ns: namespace, model: Model, filter_attrib_names: list
) -> RequestParser:
    attribs_parser = ns.parser()
    model_attributes = model.resolved
    for attrib in filter_attrib_names:
        if attrib not in model_attributes:
            raise ValueError(
                f"{attrib} is not a valid filter attribute for {model.name}"
            )

        attribs_parser.add_argument(
            attrib,
            required=False,
            store_missing=False,
            help="(Filter) %s " % model_attributes[attrib].description,
            location='args',
        )

    return attribs_parser


# Custom fields
class NullableString(fields.String):
    __schema_type__ = ['string', 'null']


class UUID(NullableString):
    def __init__(self, *args, **kwargs):
        super(UUID, self).__init__(*args, **kwargs)
        self.pattern = r"^(|%s)$" % UUID_REGEX


common_fields = {
    'id': UUID(
        title='Identifier',
        readOnly=True,
        required=True,
        description='The unique identifier',
        example=faker.uuid4(),
    ),
    'tenant_id': UUID(
        title='Identifier of Tenant',
        readOnly=True,
        required=True,
        description='Tenant it belongs to',
        example=faker.uuid4(),
    ),
    'deleted': UUID(
        readOnly=True,
        required=True,
        title='Last event Identifier',
        description='Last event over this resource',
    ),
}


def init_app(app: Flask):
    api.init_app(app)

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

    from time_tracker_api.technologies import technologies_namespace

    api.add_namespace(technologies_namespace.ns)

    from time_tracker_api.users import users_namespace

    api.add_namespace(users_namespace.ns)


"""
Error handlers
"""


@api.errorhandler(CosmosResourceExistsError)
def handle_cosmos_resource_exists_error(error):
    app.logger.error(error)
    return {'message': 'It already exists'}, HTTPStatus.CONFLICT


@api.errorhandler(CosmosResourceNotFoundError)
@api.errorhandler(StopIteration)
def handle_not_found_errors(error):
    app.logger.error(error)
    return {'message': 'It was not found'}, HTTPStatus.NOT_FOUND


@api.errorhandler(CosmosHttpResponseError)
def handle_cosmos_http_response_error(error):
    app.logger.error(error)
    return (
        {'message': 'Invalid request. Please verify your data.'},
        HTTPStatus.BAD_REQUEST,
    )


@api.errorhandler(AttributeError)
def handle_attribute_error(error):
    app.logger.error(error)
    return (
        {'message': "There are missing attributes"},
        HTTPStatus.UNPROCESSABLE_ENTITY,
    )


@api.errorhandler(CustomError)
def handle_custom_error(error):
    app.logger.error(error)
    return {'message': error.description}, error.code


@api.errorhandler
def default_error_handler(error):
    app.logger.error(error)
    return (
        {'message': 'An unhandled exception occurred.'},
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )

@api.errorhandler(StopIteration)
def handle_no_content(error):
    app.logger.error(error)
    return {'message': 'No Content'}, HTTPStatus.NO_CONTENT


