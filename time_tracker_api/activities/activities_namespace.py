from flask_restplus import fields, Resource, Namespace
from time_tracker_api.api import audit_fields
from faker import Faker

faker = Faker()

ns = Namespace('activities', description='API for activities')

# Activity Model
activity_input = ns.model('ActivityInput', {
    'name': fields.String(
        required=True,
        title='Name',
        max_length=50,
        description='Canonical name of the activity',
        example=faker.word(['Development', 'Training']),
    ),
    'description': fields.String(
        title='Description',
        description='Comments about the activity',
        example=faker.paragraph(),
    ),
})

activity_response_fields = {
    'id': fields.String(
        readOnly=True,
        required=True,
        title='Identifier',
        description='The unique identifier',
        example=faker.random_int(1, 9999),
    )
}
activity_response_fields.update(audit_fields)

activity = ns.inherit(
    'Activity',
    activity_input,
    activity_response_fields
)


@ns.route('')
class Activities(Resource):
    @ns.doc('list_activities')
    @ns.marshal_list_with(activity, code=200)
    def get(self):
        """List all available activities"""
        return []

    @ns.doc('create_activity')
    @ns.expect(activity_input)
    @ns.marshal_with(activity, code=201)
    @ns.response(400, 'Invalid format of the attributes of the activity.')
    def post(self):
        """Create a single activity"""
        return ns.payload, 201


@ns.route('/<string:id>')
@ns.response(404, 'Activity not found')
@ns.param('id', 'The unique identifier of the activity')
class Activity(Resource):
    @ns.doc('get_activity')
    @ns.marshal_with(activity)
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
    @ns.expect(activity_input)
    @ns.marshal_with(activity)
    def put(self, id):
        """Updates an activity"""
        return ns.payload
