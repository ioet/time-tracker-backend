from faker import Faker
from flask_restplus import fields, Resource, Namespace

from time_tracker_api.api import audit_fields

faker = Faker()

ns = Namespace('time-entries', description='API for time entries')

# TimeEntry Model
time_entry_input = ns.model('TimeEntryInput', {
    'project_id': fields.String(
        required=True,
        title='Project',
        max_length=64,
        description='The id of the selected project',
        example=faker.random_int(1, 9999),
    ),
    'activity_id': fields.String(
        required=False,
        title='Activity',
        max_length=64,
        description='The id of the selected activity',
        example=faker.random_int(1, 9999),
    ),
    'technologies': fields.List(
        fields.String(
            required=True,
            title='Technologies',
            max_length=64,
            description='Technology names used in this time-entry',
        ),
        example=faker.words(
            3,
            ['java', 'elixir', 'python', 'docker'],
            unique=True
        )
    ),
    'description': fields.String(
        title='Comments',
        description='Comments about the time entry',
        example=faker.paragraph(),
    ),
    'start_date': fields.DateTime(
        required=True,
        title='Start date',
        description='When the user started doing this activity',
        example=faker.iso8601(end_datetime=None),
    ),
    'end_date': fields.DateTime(
        required=True,
        title='End date',
        description='When the user ended doing this activity',
        example=faker.iso8601(end_datetime=None),
    ),
})

time_entry_response_fields = {
    'id': fields.String(
        readOnly=True,
        required=True,
        title='Identifier',
        description='The unique identifier',
        example=faker.random_int(1, 9999),
    ),
    'running': fields.Boolean(
        readOnly=True,
        title='Is it running?',
        description='Whether this time entry is currently running or not',
        example=faker.boolean(),
    ),
}
time_entry_response_fields.update(audit_fields)

time_entry = ns.inherit(
    'TimeEntry',
    time_entry_input,
    time_entry_response_fields,
)


@ns.route('')
class TimeEntries(Resource):
    @ns.doc('list_time_entries')
    @ns.marshal_list_with(time_entry, code=200)
    def get(self):
        return [], 200

    @ns.doc('create_time_entry')
    @ns.expect(time_entry_input)
    @ns.marshal_with(time_entry, code=201)
    @ns.response(400, 'Invalid format of the attributes of the time entry')
    def post(self):
        return ns.payload, 201


@ns.route('/<string:id>')
@ns.response(404, 'Time entry not found')
@ns.param('id', 'The unique identifier of the time entry')
class TimeEntry(Resource):
    @ns.doc('get_time_entry')
    @ns.marshal_with(time_entry)
    def get(self, id):
        return {}

    @ns.doc('delete_time_entry')
    @ns.response(204, 'The time entry was deleted successfully (No content is returned)')
    def delete(self, id):
        return None, 204

    @ns.doc('put_time_entry')
    @ns.response(400, 'Invalid format of the attributes of the time entry.')
    @ns.expect(time_entry_input)
    @ns.marshal_with(time_entry)
    def put(self, id):
        return ns.payload


@ns.route('/<string:id>/stop')
@ns.response(404, 'Running time entry not found')
@ns.param('id', 'The unique identifier of a running time entry')
class StopTimeEntry(Resource):
    @ns.doc('stop_time_entry')
    @ns.response(204, 'The time entry was stopped successfully (No content is returned)')
    def post(self, id):
        return None, 204


@ns.route('/<string:id>/continue')
@ns.response(404, 'Stopped time entry not found')
@ns.param('id', 'The unique identifier of a stopped time entry')
class ContinueTimeEntry(Resource):
    @ns.doc('continue_time_entry')
    @ns.response(204, 'The time entry was continued successfully (No content is returned)')
    def post(self, id):
        return None, 204
