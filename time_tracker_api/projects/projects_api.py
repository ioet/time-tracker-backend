from flask_restplus import Namespace, Resource, abort, inputs
from .projects_model import project_dao
from time_tracker_api.errors import MissingResource

ns = Namespace('projects', description='API for projects (clients)')

@ns.route('/')
class Projects(Resource):
    @ns.doc('list_projects')
    def get(self):
        """List all projects"""
        return project_dao.get_all(), 200

    @ns.doc('create_project')
    def post(self):
        """Create a project"""
        return project_dao.create(ns.payload), 201

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
    def get(self, uid):
        """Retrieve a project"""
        return project_dao.get(uid)

    @ns.doc('delete_project')
    @ns.response(204, 'Project deleted')
    def delete(self, uid):
        """Deletes a project"""
        project_dao.delete(uid)
        return None, 204

    @ns.doc('put_project')
    def put(self, uid):
        """Create or replace a project"""
        return project_dao.update(uid, ns.payload)

    @ns.doc('update_project_status')
    @ns.param('uid', 'The project identifier')
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
