from faker import Faker
from flask_restplus import Namespace, Resource, fields
from flask_restplus._http import HTTPStatus
from flask import request

from time_tracker_api.api import common_fields, UUID_REGEX
from time_tracker_api.project_types.project_types_model import create_dao

faker = Faker()

ns = Namespace('project-types', description='API for project types')

# ProjectType Model
project_type_input = ns.model('ProjectTypeInput', {
    'name': fields.String(
        title='Name',
        required=True,
        max_length=50,
        description='Name of the project type',
        example=faker.random_element(["Customer","Training","Internal"]),
    ),
    'description': fields.String(
        title='Description',
        required=False,
        max_length=250,
        description='Comments about the project type',
        example=faker.paragraph(),
    ),
    'customer_id': fields.String(
        title='Identifier of the Customer',
        required=False,
        description='Customer this project type belongs to. '
                    'If not specified, it will be considered an internal project of the tenant.',
        pattern=UUID_REGEX,
        example=faker.uuid4(),
    ),
    'parent_id': fields.String(
        title='Identifier of the parent project type',
        required=False,
        description='This parent node allows to created a tree-like structure for project types',
        pattern=UUID_REGEX,
        example=faker.uuid4(),
    ),
})

project_type_response_fields = {}
project_type_response_fields.update(common_fields)

project_type = ns.inherit(
    'ProjectType',
    project_type_input,
    project_type_response_fields
)

project_type_dao = create_dao()


@ns.route('')
class ProjectTypes(Resource):
    @ns.doc('list_project_types')
    @ns.marshal_list_with(project_type)
    def get(self):
        """List all project types"""
        return project_type_dao.get_all(conditions=request.args)

    @ns.doc('create_project_type')
    @ns.response(HTTPStatus.CONFLICT, 'This project type already exists')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid format or structure '
                                         'of the attributes of the project type')
    @ns.expect(project_type_input)
    @ns.marshal_with(project_type, code=HTTPStatus.CREATED)
    def post(self):
        """Create a project type"""
        return project_type_dao.create(ns.payload), HTTPStatus.CREATED


@ns.route('/<string:id>')
@ns.response(HTTPStatus.NOT_FOUND, 'This project type does not exist')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The data has an invalid format')
@ns.param('id', 'The project type identifier')
class ProjectType(Resource):
    @ns.doc('get_project_type')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
    @ns.marshal_with(project_type)
    def get(self, id):
        """Get a project type"""
        return project_type_dao.get(id)

    @ns.doc('update_project_type')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid format or structure '
                                         'of the attributes of the project type')
    @ns.response(HTTPStatus.CONFLICT, 'A project type already exists with this new data')
    @ns.expect(project_type_input)
    @ns.marshal_with(project_type)
    def put(self, id):
        """Update a project type"""
        return project_type_dao.update(id, ns.payload)

    @ns.doc('delete_project_type')
    @ns.response(HTTPStatus.NO_CONTENT, 'Project Type successfully deleted')
    def delete(self, id):
        """Delete a project type"""
        project_type_dao.delete(id)
        return None, HTTPStatus.NO_CONTENT
