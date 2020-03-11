from flask_restplus import fields, Resource, Namespace

ns = Namespace('activities', description='API for activities')

# Activity Model
activity = ns.model('Activity', {
    'name': fields.String(
        required=True,
        title='Name',
        max_length=50,
        description='Canonical name of the activity',
    ),
    'description': fields.String(
        title='Description',
        description='Comments about the activity',
    ),
})

activity_response = ns.inherit('ActivityResponse', activity, {
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
class Activities(Resource):
    @ns.doc('list_activities')
    @ns.marshal_list_with(activity_response, code=200)
    def get(self):
        """List all available activities"""
        return []

    @ns.doc('create_activity')
    @ns.expect(activity)
    @ns.marshal_with(activity_response, code=201)
    @ns.response(400, 'Invalid format of the attributes of the activity.')
    def post(self):
        """Create a single activity"""
        return ns.payload, 201


@ns.route('/<string:id>')
@ns.response(404, 'Activity not found')
@ns.param('id', 'The unique identifier of the activity')
class Activity(Resource):
    @ns.doc('get_activity')
    @ns.marshal_with(activity_response)
    def get(self, id):
        """Retrieve all the data of a single activity"""
        return {}

    @ns.doc('delete_activity')
    @ns.response(204, 'The activity was deleted successfully (No content is returned)')
    def delete(self, id):
        """Deletes a activity"""
        return None, 204

    @ns.doc('put_activity')
    @ns.response(400, 'Invalid format of the attributes of the activity.')
    @ns.expect(activity)
    @ns.marshal_with(activity_response)
    def put(self, id):
        """Updates an activity"""
        return ns.payload
