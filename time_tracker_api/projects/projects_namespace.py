from faker import Faker
from flask_restplus import Namespace, Resource, fields
from flask_restplus._http import HTTPStatus

from time_tracker_api.api import audit_fields
from time_tracker_api.projects.projects_model import PROJECT_TYPE, create_dao

faker = Faker()

ns = Namespace('projects', description='API for projects (clients)')

# Project Model
project_input = ns.model('ProjectInput', {
    'name': fields.String(
        required=True,
        title='Name',
        max_length=50,
        description='Name of the project',
        example=faker.company(),
    ),
    'description': fields.String(
        title='Description',
        max_length=250,
        description='Description about the project',
        example=faker.paragraph(),
    ),
    'type': fields.String(
        required=False,
        title='Type',
        max_length=10,
        description='If it is `Costumer`, `Training` or other type',
        enum=PROJECT_TYPE.valid_type_values(),
        example=faker.word(PROJECT_TYPE.valid_type_values()),
    ),
    'active': fields.Boolean(
        title='Is active?',
        description='Whether the project is active or not',
        default=True,
        example=faker.boolean(),
    ),
})

project_response_fields = {
    'id': fields.String(
        readOnly=True,
        required=True,
        title='Identifier',
        description='The unique identifier',
        example=faker.random_int(1, 9999),
    )
}
project_response_fields.update(audit_fields)

project = ns.inherit(
    'Project',
    project_input,
    project_response_fields
)

project_dao = create_dao()


@ns.route('')
class Projects(Resource):
    @ns.doc('list_projects')
    @ns.marshal_list_with(project)
    def get(self):
        """List all projects"""
        return project_dao.get_all()

    @ns.doc('create_project')
    @ns.response(HTTPStatus.CONFLICT, 'This project already exists')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid format or structure '
                                         'of the attributes of the project')
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
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
    @ns.marshal_with(project)
    def get(self, id):
        """Get a project"""
        return project_dao.get(id)

    @ns.doc('update_project')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid format or structure '
                                         'of the attributes of the project')
    @ns.response(HTTPStatus.CONFLICT, 'A project already exists with this new data')
    @ns.expect(project_input)
    @ns.marshal_with(project)
    def put(self, id):
        """Update a project"""
        return project_dao.update(id, ns.payload)

    @ns.doc('delete_project')
    @ns.response(HTTPStatus.NO_CONTENT, 'Project successfully deleted')
    def delete(self, id):
        """Delete a project"""
        project_dao.delete(id)
        return None, HTTPStatus.NO_CONTENT
