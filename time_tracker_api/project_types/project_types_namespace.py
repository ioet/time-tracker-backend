from faker import Faker
from flask_restplus import Namespace, Resource, fields
from flask_restplus._http import HTTPStatus

from time_tracker_api.api import common_fields
from time_tracker_api.project_types.project_types_model import create_dao

faker = Faker()

ns = Namespace('project-types', description='API for project types')

# ProjectType Model
project_type_input = ns.model('ProjectTypeInput', {
    'name': fields.String(
        required=True,
        title='Name',
        max_length=50,
        description='Name of the project type',
        example=faker.random_element(["Customer","Training","Internal"]),
    ),
    'description': fields.String(
        title='Description',
        max_length=250,
        description='Description about the project type',
        example=faker.paragraph(),
    ),
    'customer_id': fields.String(
        title='Identifier of the Customer',
        description='Customer this project type belongs to',
        example=faker.uuid4(),
    ),
    'parent_id': fields.String(
        title='Identifier of Parent of the project type',
        description='Defines a self reference of the model ProjectType',
        example=faker.uuid4(),
    ),
})

project_type_response_fields = {
    'id': fields.String(
        readOnly=True,
        required=True,
        title='Identifier',
        description='The unique identifier',
        example=faker.uuid4(),
    ),
    'tenant_id': fields.String(
        required=True,
        title='Identifier of Tenant',
        description='Tenant this project type belongs to',
        example=faker.uuid4(),
    ),
}
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
        return project_type_dao.get_all()

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
