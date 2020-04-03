from datetime import datetime

from faker import Faker
from flask_restplus import fields, Resource, Namespace
from flask_restplus._http import HTTPStatus

from time_tracker_api.api import audit_fields
from time_tracker_api.database import COMMENTS_MAX_LENGTH
from time_tracker_api.time_entries.time_entries_model import create_dao

faker = Faker()

ns = Namespace('time-entries', description='API for time entries')

# TimeEntry Model
time_entry_input = ns.model('TimeEntryInput', {
    'project_id': fields.String(
        required=True,
        title='Project',
        description='The id of the selected project',
        example=faker.uuid4(),
    ),
    'activity_id': fields.String(
        required=True,
        title='Activity',
        description='The id of the selected activity',
        example=faker.uuid4(),
    ),
    'description': fields.String(
        title='Comments',
        description='Comments about the time entry',
        example=faker.paragraph(nb_sentences=2),
        max_length=COMMENTS_MAX_LENGTH,
    ),
    'start_date': fields.DateTime(
        required=True,
        title='Start date',
        description='When the user started doing this activity',
        example=faker.iso8601(end_datetime=None),
    ),
    'end_date': fields.DateTime(
        title='End date',
        description='When the user ended doing this activity',
        example=faker.iso8601(end_datetime=None),
    ),
    'uri': fields.String(
        title='Uniform Resource identifier',
        description='Either identifier or locator',
        example=faker.words(
            1,
            ['http://example.com/mypage.html', '/some/page.html']
        ),
    ),
    'owner_id': fields.String(
        required=True,
        title='Owner of time entry',
        description='User who owns the time entry',
        example=faker.uuid4(),
    ),
    'tenant_id': fields.String(
        required=True,
        title='Identifier of Tenant',
        description='Tenant this project belongs to',
        example=faker.uuid4(),
    ),
})

time_entry_response_fields = {
    'id': fields.String(
        readOnly=True,
        title='Identifier',
        description='The unique identifier',
        example=faker.uuid4(),
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

time_entries_dao = create_dao()


@ns.route('')
class TimeEntries(Resource):
    @ns.doc('list_time_entries')
    @ns.marshal_list_with(time_entry)
    def get(self):
        """List all time entries"""
        return time_entries_dao.get_all()

    @ns.doc('create_time_entry')
    @ns.expect(time_entry_input)
    @ns.marshal_with(time_entry, code=HTTPStatus.CREATED)
    @ns.response(HTTPStatus.CONFLICT, 'This time entry already exists')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid format or structure '
                                         'of the attributes of the time entry')
    def post(self):
        """Create a time entry"""
        return time_entries_dao.create(ns.payload), HTTPStatus.CREATED


@ns.route('/<string:id>')
@ns.response(HTTPStatus.NOT_FOUND, 'This time entry does not exist')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
@ns.param('id', 'The unique identifier of the time entry')
class TimeEntry(Resource):
    @ns.doc('get_time_entry')
    @ns.marshal_with(time_entry)
    def get(self, id):
        """Get a time entry"""
        return time_entries_dao.get(id)

    @ns.doc('put_time_entry')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid format or structure '
                                         'of the attributes of the time entry')
    @ns.response(HTTPStatus.CONFLICT, 'A time entry already exists with this new data or there'
                                      ' is a bad reference for the project or activity')
    @ns.expect(time_entry_input)
    @ns.marshal_with(time_entry)
    def put(self, id):
        """Update a time entry"""
        return time_entries_dao.update(id, ns.payload)

    @ns.doc('delete_time_entry')
    @ns.response(HTTPStatus.NO_CONTENT, 'Time entry successfully deleted')
    def delete(self, id):
        """Delete a time_entry"""
        time_entries_dao.delete(id)
        return None, HTTPStatus.NO_CONTENT


@ns.route('/<string:id>/stop')
@ns.response(HTTPStatus.NOT_FOUND, 'Running time entry not found')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
@ns.param('id', 'The unique identifier of a running time entry')
class StopTimeEntry(Resource):
    @ns.doc('stop_time_entry')
    @ns.marshal_with(time_entry)
    def post(self, id):
        """Stop a running time entry"""
        return time_entries_dao.update(id, {
            'end_date': datetime.utcnow()
        })


@ns.route('/<string:id>/restart')
@ns.response(HTTPStatus.NOT_FOUND, 'Stopped time entry not found')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format.')
@ns.param('id', 'The unique identifier of a stopped time entry')
class RestartTimeEntry(Resource):
    @ns.doc('restart_time_entry')
    @ns.marshal_with(time_entry)
    def post(self, id):
        """Restart a time entry"""
        return time_entries_dao.update(id, {
            'end_date': None
        })
