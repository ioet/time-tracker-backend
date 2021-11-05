from faker import Faker
from flask_restplus import fields, Resource
from flask_restplus._http import HTTPStatus

from time_tracker_api.activities.activities_model import create_dao
from time_tracker_api.api import (
    common_fields,
    api,
    remove_required_constraint,
    NullableString,
)
from utils.enums.status import Status

faker = Faker()

ns = api.namespace(
    'activities', description='Namespace of the API for activities'
)

# Activity Model
activity_input = ns.model(
    'ActivityInput',
    {
        'name': fields.String(
            required=True,
            title='Name',
            max_length=50,
            description='Canonical name of the activity',
            example=faker.word(['Development', 'Training']),
        ),
        'description': NullableString(
            title='Description',
            required=False,
            description='Comments about the activity',
            example=faker.paragraph(),
        ),
        'status': fields.String(
            required=False,
            title='Status',
            description='Status active or inactive activities',
            example=Faker().words(
                2,
                [
                    Status.ACTIVE.value,
                    Status.INACTIVE.value,
                ],
                unique=True,
            ),
        ),
    },
)

activity_response_fields = {}
activity_response_fields.update(common_fields)

activity = ns.inherit('Activity', activity_input, activity_response_fields)

activity_dao = create_dao()

list_activities_attribs_parser = ns.parser()
list_activities_attribs_parser.add_argument(
    'status',
    required=False,
    store_missing=False,
    help="(Filter) Permits to get a list of active or inactive activities.",
    location='args',
)


@ns.route('')
class Activities(Resource):
    @ns.doc('list_activities')
    @ns.marshal_list_with(activity)
    @ns.expect(list_activities_attribs_parser)
    def get(self):
        """List all activities"""
        conditions = list_activities_attribs_parser.parse_args()
        return activity_dao.get_all(conditions=conditions)

    @ns.doc('create_activity')
    @ns.response(HTTPStatus.CONFLICT, 'This activity already exists')
    @ns.response(
        HTTPStatus.BAD_REQUEST,
        'Invalid format or structure of the attributes of the activity',
    )
    @ns.expect(activity_input)
    @ns.marshal_with(activity, code=HTTPStatus.CREATED)
    def post(self):
        """Create an activity"""
        return activity_dao.create(ns.payload), HTTPStatus.CREATED


@ns.route('/<string:id>')
@ns.response(HTTPStatus.NOT_FOUND, 'Activity not found')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
@ns.param('id', 'The activity identifier')
class Activity(Resource):
    @ns.doc('get_activity')
    @ns.marshal_with(activity)
    def get(self, id):
        """Get an activity"""
        return activity_dao.get(id)

    @ns.doc('update_activity')
    @ns.expect(remove_required_constraint(activity_input))
    @ns.response(
        HTTPStatus.BAD_REQUEST, 'Invalid format or structure of the activity'
    )
    @ns.response(
        HTTPStatus.CONFLICT, 'An activity already exists with this new data'
    )
    @ns.marshal_with(activity)
    def put(self, id):
        """Update an activity"""
        return activity_dao.update(id, ns.payload)

    @ns.doc('delete_activity')
    @ns.response(HTTPStatus.NO_CONTENT, 'Activity deleted successfully')
    def delete(self, id):
        """Delete an activity"""
        activity_dao.update(id, {'status': Status.INACTIVE.value})
        return None, HTTPStatus.NO_CONTENT
