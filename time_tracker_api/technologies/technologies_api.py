from flask_restplus import Namespace, Resource, fields

ns = Namespace('technologies', description='API for technologies used')

# Technology Model
technology = ns.model('Technology', {
    'id': fields.String(
        readOnly=True,
        required=True,
        title='Identifier',
        description='The unique id of the technology'
    ),
    'tenant_id': fields.String(
        required=True,
        title='Tenant',
        max_length=64,
        description='The tenant this technology belongs to'
    ),
    'name': fields.String(
        required=True,
        title='Name',
        max_length=50,
        description='Name of the technology'
    ),
    'created_at': fields.Date(
        title='Date',
        description='Date of creation'
    ),
    'created_by': fields.String(
        required=True,
        title='Type',
        max_length=30,
        description='Id of user who first added this technology',
    ),
})


@ns.route('')
class Technologies(Resource):
    @ns.doc('list_technologies')
    @ns.marshal_list_with(technology, code=200)
    def get(self):
        """List all technologies"""
        return [], 200

    @ns.doc('create_technology')
    @ns.expect(technology)
    @ns.marshal_with(technology, code=201)
    def post(self):
        """Create a technology"""
        return ns.payload, 201


@ns.route('/<string:uid>')
@ns.response(404, 'Technology not found')
@ns.param('uid', 'The technology identifier')
class Technology(Resource):
    @ns.doc('get_technology')
    @ns.marshal_with(technology)
    def get(self, uid):
        """Retrieve a technology"""
        return {}

    @ns.doc('update_technology_status')
    @ns.param('uid', 'The technology identifier')
    @ns.expect(technology)
    @ns.response(204, 'State of the technology successfully updated')
    def post(self, uid):
        """Updates a technology using form data"""
        return ns.payload()

    @ns.doc('put_technology')
    @ns.expect(technology)
    @ns.marshal_with(technology)
    def put(self, uid):
        """Create or replace a technology"""
        return ns.payload()

    @ns.doc('delete_technology')
    @ns.response(204, 'Technology deleted successfully')
    def delete(self, uid):
        """Deletes a technology"""
        return None, 204
