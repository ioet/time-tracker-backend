from faker import Faker
from flask_restplus import Resource, fields
from flask_restplus._http import HTTPStatus

from time_tracker_api.api import (
    common_fields,
    create_attributes_filter,
    UUID,
    api,
    remove_required_constraint,
    NullableString,
)
from time_tracker_api.projects.projects_model import create_dao

faker = Faker()

ns = api.namespace('projects', description='Namespace of the API for projects')

# Project Model
project_input = ns.model(
    'ProjectInput',
    {
        'name': fields.String(
            required=True,
            title='Name',
            max_length=50,
            description='Name of the project',
            example=faker.company(),
        ),
        'description': NullableString(
            title='Description',
            required=False,
            max_length=250,
            description='Description about the project',
            example=faker.paragraph(),
        ),
        'customer_id': UUID(
            title='Identifier of the Customer',
            required=False,
            description='Customer this project type belongs to. '
            'If not specified, it will be considered an internal project of the tenant.',
            example=faker.uuid4(),
        ),
        'project_type_id': UUID(
            title='Identifier of the project type',
            required=False,
            description='Id of the project type it belongs. This allows grouping the projects.',
            example=faker.uuid4(),
        ),
        'technologies': fields.List(
            fields.String,
            title='List of technologies this project involves',
            required=False,
            description='List of technologies this project involves',
            example="['python', 'restplus', 'openapi']",
        ),
        'status': fields.String(
            required=False,
            title='Status',
            description='Status active or inactive projects',
            example=Faker().words(
                2,
                [
                    'active',
                    'inactive',
                ],
                unique=True,
            ),
        ),
    },
)

project_type_nested_field = ns.model('ProjectType', {
    'name': fields.String(
        title='Name',
        required=True,
        max_length=50,
        description='Name of the project type',
        example=faker.random_element(["Customer", "Training", "Internal"]),
    ),
    'description': NullableString(
        title='Description',
        required=False,
        max_length=250,
        description='Comments about the project type',
        example=faker.paragraph(),
    )
})

customer_nested_field = ns.model('Customer', {
    'name': fields.String(
        title='Name',
        required=True,
        max_length=50,
        description='Name of the customer',
        example=faker.company(),
    ),
    'description': NullableString(
        title='Description',
        required=False,
        max_length=250,
        description='Description about the customer',
        example=faker.paragraph(),
    )
})

project_response_fields = {
    # TODO: Remove this DEAD CODE
    'customer_name': fields.String(
        required=True,
        title='Customer Name',
        max_length=50,
        description='Name of the customer of the project',
        example=faker.company(),
    ),
    'customer': fields.Nested(customer_nested_field),
    'project_type': fields.Nested(project_type_nested_field),
}
project_response_fields.update(common_fields)

project = ns.inherit('Project', project_input, project_response_fields)

project_dao = create_dao()

attributes_filter = create_attributes_filter(
    ns, project, ["customer_id", "project_type_id", "status"]
)


@ns.route('')
class Projects(Resource):
    @ns.doc('list_projects')
    @ns.expect(attributes_filter)
    @ns.marshal_list_with(project)
    def get(self):
        """List all projects"""
        conditions = attributes_filter.parse_args()
        return project_dao.get_all(conditions=conditions)

    @ns.doc('create_project')
    @ns.response(HTTPStatus.CONFLICT, 'This project already exists')
    @ns.response(
        HTTPStatus.BAD_REQUEST,
        'Invalid format or structure ' 'of the attributes of the project',
    )
    @ns.expect(project_input)
    @ns.marshal_with(project, code=HTTPStatus.CREATED)
    def post(self):
        """Create a project"""
        return project_dao.create(ns.payload), HTTPStatus.CREATED


@ns.route('/<string:id>')
@ns.response(HTTPStatus.NOT_FOUND, 'This project does not exist')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The data has an invalid format')
@ns.param('id', 'The project identifier')
class Project(Resource):
    @ns.doc('get_project')
    @ns.response(
        HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format'
    )
    @ns.marshal_with(project)
    def get(self, id):
        """Get a project"""
        return project_dao.get(id)

    @ns.doc('update_project')
    @ns.response(
        HTTPStatus.BAD_REQUEST,
        'Invalid format or structure ' 'of the attributes of the project',
    )
    @ns.response(
        HTTPStatus.CONFLICT, 'A project already exists with this new data'
    )
    @ns.expect(remove_required_constraint(project_input))
    @ns.marshal_with(project)
    def put(self, id):
        """Update a project"""
        return project_dao.update(id, ns.payload)

    @ns.doc('delete_project')
    @ns.response(HTTPStatus.NO_CONTENT, 'Project successfully deleted')
    def delete(self, id):
        """Delete a project"""
        project_dao.update(id, {'status': 'inactive'})
        return None, HTTPStatus.NO_CONTENT
