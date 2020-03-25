from faker import Faker
from flask_restplus import fields, Resource, Namespace

from time_tracker_api import flask_app
from time_tracker_api.api import audit_fields
from time_tracker_api.activities.activities_model import create_dao

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

activity_dao = create_dao(flask_app)


@ns.route('')
class Activities(Resource):
    @ns.doc('list_activities')
    @ns.marshal_list_with(activity, code=200)
    def get(self):
        """List all activities"""
        return activity_dao.get_all(), 200

    @ns.doc('create_activity')
    @ns.response(400, 'Bad request')
    @ns.expect(activity_input)
    @ns.marshal_with(activity, code=201)
    def post(self):
        """Create an activity"""
        return activity_dao.create(ns.payload), 201


@ns.route('/<string:id>')
@ns.response(404, 'Activity not found')
@ns.param('id', 'The activity identifier')
class Activity(Resource):
    @ns.doc('get_activity')
    @ns.response(422, 'The id has an invalid format')
    @ns.marshal_with(activity, code=200)
    def get(self, id):
        """Get an activity"""
        return activity_dao.get(id)

    @ns.doc('update_activity')
    @ns.response(422, 'The data has an invalid format.')
    @ns.expect(activity_input)
    @ns.marshal_with(activity)
    def put(self, id):
        """Update an activity"""
        return activity_dao.update(id, ns.payload)

    @ns.doc('delete_activity')
    @ns.response(422, 'The id has an invalid format')
    @ns.response(204, 'Activity deleted successfully')
    def delete(self, id):
        """Delete an activity"""
        activity_dao.delete(id)
        return None, 204
