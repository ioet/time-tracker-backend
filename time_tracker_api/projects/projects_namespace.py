from flask_restplus import Namespace, Resource, abort, inputs, fields
from .projects_model import project_dao
from time_tracker_api.errors import MissingResource
from time_tracker_api.api import audit_fields

ns = Namespace('projects', description='API for projects (clients)')

# Project Model
project_input = ns.model('ProjectInput', {
    'name': fields.String(
        required=True,
        title='Name',
        max_length=50,
        description='Name of the project'
    ),
    'description': fields.String(
        title='Description',
        description='Description about the project'
    ),
    'type': fields.String(
        required=True,
        title='Type',
        max_length=30,
        description='If it is `Costumer`, `Training` or other type',
    ),
})

project_response_fields = {
    'id': fields.String(
        readOnly=True,
        required=True,
        title='Identifier',
        description='The unique identifier',
    )
}
project_response_fields.update(audit_fields)

project = ns.inherit(
    'Project',
    project_input,
    project_response_fields
)


@ns.route('')
class Projects(Resource):
    @ns.doc('list_projects')
    @ns.marshal_list_with(project, code=200)
    def get(self):
        """List all projects"""
        return project_dao.get_all(), 200

    @ns.doc('create_project')
    @ns.expect(project_input)
    @ns.marshal_with(project, code=201)
    def post(self):
        """Create a project"""
        return project_dao.create(ns.payload), 201

# TODO : fix, this parser is for a field that is not being used.
project_update_parser = ns.parser()
project_update_parser.add_argument('active',
                                   type=inputs.boolean,
                                   location='form',
                                   required=True,
                                   help='Is the project active?')


@ns.route('/<string:uid>')
@ns.response(404, 'Project not found')
@ns.param('uid', 'The project identifier')
class Project(Resource):
    @ns.doc('get_project')
    @ns.marshal_with(project)
    def get(self, uid):
        """Retrieve a project"""
        return project_dao.get(uid)

    @ns.doc('update_project_status')
    @ns.expect(project)
    @ns.response(204, 'State of the project successfully updated')
    def post(self, uid):
        """Updates a project using form data"""
        try:
            update_data = project_update_parser.parse_args()
            return project_dao.update(uid, update_data), 200
        except ValueError:
            abort(code=400)
        except MissingResource as e:
            abort(message=str(e), code=404)

    @ns.doc('put_project')
    @ns.expect(project_input)
    @ns.marshal_with(project)
    def put(self, uid):
        """Create or replace a project"""
        return project_dao.update(uid, ns.payload)

    @ns.doc('delete_project')
    @ns.response(204, 'Project deleted successfully')
    def delete(self, uid):
        """Deletes a project"""
        project_dao.delete(uid)
        return None, 204
