from faker import Faker
from flask_restplus import Namespace, Resource, fields

from time_tracker_api.api import audit_fields

faker = Faker()

ns = Namespace('technologies', description='API for technologies used')

# Technology Model
technology_input = ns.model('TechnologyInput', {
    'name': fields.String(
        required=True,
        title='Name',
        max_length=50,
        description='Name of the technology',
        example=faker.word(['Java', 'Python', 'Elixir'])
    ),
})

technology_response_fields = {
    'id': fields.String(
        readOnly=True,
        required=True,
        title='Identifier',
        description='The unique identifier',
        example=faker.random_int(1, 9999),
    ),
}
technology_response_fields.update(audit_fields)

technology = ns.inherit(
    'Technology',
    technology_input,
    technology_response_fields
)


@ns.route('')
class Technologies(Resource):
    @ns.doc('list_technologies')
    @ns.marshal_list_with(technology, code=200)
    def get(self):
        """List all technologies"""
        return [], 200

    @ns.doc('create_technology')
    @ns.expect(technology_input)
    @ns.marshal_with(technology, code=201)
    def post(self):
        """Create a technology"""
        return ns.payload, 201


@ns.route('/<string:id>')
@ns.response(404, 'Technology not found')
@ns.param('id', 'The technology identifier')
class Technology(Resource):
    @ns.doc('get_technology')
    @ns.marshal_with(technology)
    def get(self, id):
        """Retrieve a technology"""
        return {}

    @ns.doc('put_technology')
    @ns.expect(technology_input)
    @ns.marshal_with(technology)
    def put(self, id):
        """Updates a technology"""
        return ns.payload()

    @ns.doc('delete_technology')
    @ns.response(204, 'Technology deleted successfully')
    def delete(self, id):
        """Deletes a technology"""
        return None, 204
