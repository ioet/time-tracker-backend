from faker import Faker
from flask_restplus import fields, Resource
from flask_restplus._http import HTTPStatus

from time_tracker_api.api import common_fields, api, NullableString
from time_tracker_api.security import current_user_id

from utils.azure_users import AzureConnection

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
        'roles': fields.List(
            fields.String(
                title='Roles',
                description='List of the roles assigned to the user by the tenant',
            ),
            example=Faker().words(
                3, ['time-tracker-admin', 'test-user', 'guest',],
            ),
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
        azure_connection = AzureConnection()
        is_current_user_a_tester = azure_connection.is_test_user(
            current_user_id()
        )
        return (
            azure_connection.users_v2()
            if is_current_user_a_tester
            else azure_connection.get_non_test_users()
        )


@ns.route('/<string:user_id>/roles/<string:role_id>/grant')
@ns.param('user_id', 'The user identifier')
@ns.param('role_id', 'The role name identifier')
class GrantRole(Resource):
    @ns.doc('grant_role')
    @ns.marshal_with(user_response_fields)
    def post(self, user_id, role_id):
        """
        Grant role to user
        Available options for `role_id`:
        ```
            - test
            - admin
        ```
        """
        return AzureConnection().update_role(user_id, role_id, is_grant=True)


@ns.route('/<string:user_id>/roles/<string:role_id>/revoke')
@ns.param('user_id', 'The user identifier')
@ns.param('role_id', 'The role name identifier')
class RevokeRole(Resource):
    @ns.doc('revoke_role')
    @ns.marshal_with(user_response_fields)
    def post(self, user_id, role_id):
        """Revoke role to user"""
        return AzureConnection().update_role(user_id, role_id, is_grant=False)
