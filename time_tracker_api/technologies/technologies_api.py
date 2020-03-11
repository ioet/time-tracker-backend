from flask_restplus import Namespace, Resource, fields

ns = Namespace('technologies', description='API for technologies used')

# Technology Model
technology = ns.model('Technology', {
    'name': fields.String(
        required=True,
        title='Name',
        max_length=50,
        description='Name of the technology'
    ),
})

technology_response = ns.inherit('TechnologyResponse', technology, {
    'id': fields.String(
        readOnly=True,
        required=True,
        title='Identifier',
        description='The unique identifier',
    ),
    'created_at': fields.Date(
        readOnly=True,
        title='Created',
        description='Date of creation'
    ),
    'created_by': fields.String(
        readOnly=True,
        title='Creator',
        max_length=64,
        description='User that created it',
    ),
    'tenant_id': fields.String(
        readOnly=True,
        title='Tenant',
        max_length=64,
        description='The tenant this belongs to',
    ),
})


@ns.route('')
class Technologies(Resource):
    @ns.doc('list_technologies')
    @ns.marshal_list_with(technology_response, code=200)
    def get(self):
        """List all technologies"""
        return [], 200

    @ns.doc('create_technology')
    @ns.expect(technology)
    @ns.marshal_with(technology_response, code=201)
    def post(self):
        """Create a technology"""
        return ns.payload, 201


@ns.route('/<string:uid>')
@ns.response(404, 'Technology not found')
@ns.param('uid', 'The technology identifier')
class Technology(Resource):
    @ns.doc('get_technology')
    @ns.marshal_with(technology_response)
    def get(self, uid):
        """Retrieve a technology"""
        return {}

    @ns.doc('put_technology')
    @ns.expect(technology)
    @ns.marshal_with(technology_response)
    def put(self, uid):
        """Updates a technology"""
        return ns.payload()

    @ns.doc('delete_technology')
    @ns.response(204, 'Technology deleted successfully')
    def delete(self, uid):
        """Deletes a technology"""
        return None, 204
