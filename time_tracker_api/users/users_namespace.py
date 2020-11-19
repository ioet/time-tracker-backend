from faker import Faker
from flask_restplus import fields, Resource
from flask_restplus._http import HTTPStatus

from time_tracker_api.api import common_fields, api, NullableString

from utils.azure_users import AzureConnection


azure_connection = AzureConnection()

ns = api.namespace('users', description='Namespace of the API for users')

# User Model

user_response_fields = ns.model(
    'User',
    {
        'name': fields.String(
            title='Name',
            max_length=50,
            description='Name of the user',
            example=Faker().word(['Marcelo', 'Sandro']),
        ),
        'email': fields.String(
            title="User's Email",
            max_length=50,
            description='Email of the user that belongs to the tenant',
            example=Faker().email(),
        ),
        'role': NullableString(
            title="User's Role",
            max_length=50,
            description='Role assigned to the user by the tenant',
            example=Faker().word(['time-tracker-admin']),
        ),
    },
)

user_response_fields.update(common_fields)

user_role_input_fields = ns.model(
    'UserRoleInput',
    {
        'role': NullableString(
            title="User's Role",
            required=True,
            max_length=50,
            description='Role assigned to the user by the tenant',
            example=Faker().word(['time-tracker-admin']),
        ),
    },
)


@ns.route('')
class Users(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_response_fields)
    def get(self):
        """List all users"""
        return azure_connection.users()


@ns.route('/<string:id>/roles')
@ns.response(HTTPStatus.NOT_FOUND, 'User not found')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
@ns.param('id', 'The user identifier')
class UserRoles(Resource):
    @ns.doc('create_user_role')
    @ns.expect(user_role_input_fields)
    @ns.response(
        HTTPStatus.BAD_REQUEST, 'Invalid format or structure of the user'
    )
    @ns.marshal_with(user_response_fields)
    def post(self, id):
        """Create user's role"""
        return azure_connection.update_user_role(id, ns.payload['role'])


@ns.route('/<string:user_id>/roles/<string:role_id>')
@ns.response(HTTPStatus.NOT_FOUND, 'User not found')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
@ns.param('user_id', 'The user identifier')
@ns.param('role_id', 'The role name identifier')
class UserRole(Resource):
    @ns.doc('delete_user_role')
    @ns.marshal_with(user_response_fields)
    def delete(self, user_id, role_id):
        """Delete user's role"""
        return azure_connection.update_user_role(user_id, role=None)
