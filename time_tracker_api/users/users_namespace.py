from faker import Faker
from flask_restplus import fields, Resource
from flask_restplus._http import HTTPStatus

from time_tracker_api.api import common_fields, api, NullableString

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
        'role': NullableString(
            title="User's Role",
            max_length=50,
            description='Role assigned to the user by the tenant',
            example=faker.word(['time-tracker-admin']),
        ),
    },
)

user_response_fields.update(common_fields)

user_input_fields = ns.model(
    'UserInput',
    {
        'role': NullableString(
            title="User's Role",
            required=True,
            max_length=50,
            description='Role assigned to the user by the tenant',
            example=faker.word(['time-tracker-admin']),
        ),
    },
)


@ns.route('')
class Users(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_response_fields)
    def get(self):
        """List all users"""
        from utils.azure_users import AzureConnection

        azure_connection = AzureConnection()
        return azure_connection.users()


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

    @ns.doc('update_user')
    @ns.expect(user_input_fields)
    @ns.response(
        HTTPStatus.BAD_REQUEST, 'Invalid format or structure of the user'
    )
    @ns.marshal_with(user_response_fields)
    def put(self, id):
        """Update an user"""
        from utils.azure_users import AzureConnection

        azure_connection = AzureConnection()
        return azure_connection.update_user_role(id, ns.payload['role'])
