from faker import Faker
from flask_restplus import fields, Resource

from time_tracker_api.api import common_fields, api
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
        'roles': fields.List(
            fields.String(
                title='Roles',
                description='List of the roles assigned to the user by the tenant',
            ),
            example=Faker().words(
                3, ['time-tracker-admin', 'test-user', 'guest',], unique=True
            ),
        ),
        'groups': fields.List(
            fields.String(
                title='Groups',
                description='List of the groups the user belongs to, assigned by the tenant',
            ),
            example=Faker().words(
                3,
                [
                    'time-tracker-admin',
                    'time-tracker-tester',
                    'time-tracker-guest',
                ],
                unique=True,
            ),
        ),
    },
)

group_name_field = fields.String(
    title='group_name',
    max_length=50,
    description='Name of the Group',
    example=Faker().word(['time-tracker-admin', 'time-tracker-tester']),
)

# Data to check if a user is in the group
user_in_group_input = ns.model(
    'UserInGroupInput', {'group_name': group_name_field},
)

user_in_group_response = ns.model(
    'UserInGroupResponse',
    {
        'value': fields.Boolean(
            readOnly=True,
            title='value',
            description='Boolean to check if a user belongs to a group',
            example=Faker().boolean(),
        )
    },
)

user_response_fields.update(common_fields)


@ns.route('/<string:id>')
@ns.param('id', 'The unique identifier of the user')
class User(Resource):
    @ns.doc('get_user')
    @ns.marshal_list_with(user_response_fields)
    def get(self, id):
        """Get an user"""
        return AzureConnection().get_user(id)


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
            azure_connection.users()
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


@ns.route('/<string:user_id>/is-member-of')
@ns.param('user_id', 'The user identifier')
class UserInGroup(Resource):
    @ns.doc('user_in_group')
    @ns.expect(user_in_group_input)
    @ns.marshal_with(user_in_group_response)
    def post(self, user_id):
        """Check if user belongs to group"""
        return AzureConnection().is_user_in_group(user_id, ns.payload)


add_user_to_group_input = ns.model(
    'AddUserToGroupInput', {'group_name': group_name_field},
)


@ns.route('/<string:user_id>/groups/add')
@ns.param('user_id', 'The user identifier')
class AddToGroup(Resource):
    @ns.doc('add_to_group')
    @ns.expect(add_user_to_group_input)
    @ns.marshal_with(user_response_fields)
    def post(self, user_id):
        """
        Add user to an EXISTING group in the Azure Tenant directory.
        Available options for `group_name`:
        ```
            - time-tracker-admin
            - time-tracker-tester
        ```
        """
        return AzureConnection().add_user_to_group(
            user_id, ns.payload['group_name']
        )


remove_user_from_group_input = ns.model(
    'RemoveUserFromGroupInput', {'group_name': group_name_field},
)


@ns.route('/<string:user_id>/groups/remove')
@ns.param('user_id', 'The user identifier')
class RemoveFromGroup(Resource):
    @ns.doc('remove_from_group')
    @ns.expect(remove_user_from_group_input)
    @ns.marshal_with(user_response_fields)
    def post(self, user_id):
        """
        Remove user from an EXISTING group in the Azure Tenant directory.
        """
        return AzureConnection().remove_user_from_group(
            user_id, ns.payload['group_name']
        )
