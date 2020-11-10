from faker import Faker
from flask_restplus import fields, Resource
from flask_restplus._http import HTTPStatus

from time_tracker_api.activities.activities_model import create_dao
from time_tracker_api.api import (
    common_fields,
    api,
    remove_required_constraint,
    NullableString,
)

faker = Faker()

ns = api.namespace('users', description='Namespace of the API for users')

# User Model

user_response_fields = ns.model(
    'User',
    {
        'name': fields.String(
            title='Name',
            max_length=50,
            description='Name of the user',
            example=faker.word(['Marcelo', 'Sandro']),
        ),
        'email': fields.String(
            title="User's Email",
            max_length=50,
            description='Email of the user that belongs to the tenant',
            example=faker.email(),
        ),
    },
)

user_response_fields.update(common_fields)

"""
activity_response_fields = {}
activity_response_fields.update(common_fields)

activity = ns.inherit(
    'Activity',
    #activity_input,
    activity_response_fields
)

activity_dao = create_dao()
"""


@ns.route('')
class Users(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_response_fields)
    def get(self):
        """List all users"""
        from utils.azure_users import AzureConnection

        azure_connection = AzureConnection()
        for u in azure_connection.users():
            print(u.name, '|', u.email)
        return azure_connection.users()
        # return activity_dao.get_all()


@ns.route('/<string:id>')
@ns.response(HTTPStatus.NOT_FOUND, 'User not found')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
@ns.param('id', 'The user identifier')
class User(Resource):
    @ns.doc('get_user')
    @ns.marshal_with(user_response_fields)
    def get(self, id):
        """Get an user"""
        return {}
        # return activity_dao.get(id)
