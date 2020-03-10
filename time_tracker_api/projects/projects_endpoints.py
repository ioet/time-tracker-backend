from flask_restplus import Namespace
from flask_restplus import Resource

ns = Namespace('projects', description='Api for resource `Projects`')


@ns.route('/')
class Projects(Resource):
    @ns.doc('list_projects')
    def get(self):
        """List all projects"""
        print("List all projects")
        return {}, 200

    @ns.doc('create_project')
    def post(self):
        """Create a project"""
        print("List all projects")
        return {}, 201


@ns.route('/<string:uid>')
@ns.response(404, 'Project not found')
@ns.param('uid', 'The project identifier')
class Project(Resource):
    @ns.doc('get_project')
    def get(self, uid):
        """Retrieve a project"""
        print("Retrieve Project")
        return {}

    @ns.doc('delete_project')
    @ns.response(204, 'Project deleted')
    def delete(self, uid):
        """Deletes a project"""
        print("Delete Project")
        return None, 204

    @ns.doc('put_project')
    def put(self, uid):
        """Create or replace a project"""
        print("Create or Replace Project")
        return {}

    @ns.doc('update_project_status')
    @ns.param('uid', 'The project identifier')
    @ns.response(204, 'State of the project successfully updated')
    def post(self, uid):
        """Updates a project using form data"""
        print("Update Project using form data")
        return {}
