from datetime import timedelta
from random import choice

from faker import Faker
from flask_restplus import fields, Resource
from flask_restplus._http import HTTPStatus

from utils.time import datetime_str, current_datetime, current_datetime_str

from commons.data_access_layer.database import COMMENTS_MAX_LENGTH
from time_tracker_api.api import (
    common_fields,
    create_attributes_filter,
    api,
    UUID,
    NullableString,
    remove_required_constraint,
)
from time_tracker_api.time_entries.time_entries_dao import create_dao
from commons.feature_flags.features_flags import FeatureFlags

faker = Faker()

ns = api.namespace(
    'time-entries', description='Namespace of the API for time entries'
)

# TimeEntry Model
time_entry_input = ns.model(
    'TimeEntryInput',
    {
        'project_id': UUID(
            title='Project',
            required=True,
            description='The id of the selected project',
            example=faker.uuid4(),
        ),
        'activity_id': UUID(
            title='Activity',
            required=False,
            description='The id of the selected activity',
            example=faker.uuid4(),
        ),
        'description': NullableString(
            title='Comments',
            required=False,
            description='Comments about the time entry',
            example=faker.paragraph(nb_sentences=2),
            max_length=COMMENTS_MAX_LENGTH,
        ),
        'start_date': fields.String(
            title='Start date',
            required=False,
            description='When the user started doing this activity',
            example=datetime_str(current_datetime() - timedelta(days=1)),
        ),
        'end_date': fields.String(
            title='End date',
            required=False,
            description='When the user ended doing this activity',
            example=current_datetime_str(),
        ),
        'uri': NullableString(
            title='Uniform Resource identifier',
            description='Either identifier or locator of a resource in the Internet that helps to understand'
            ' what this time entry was about. For example, A Jira ticket, a Github issue, a Google document.',
            required=False,
            example=faker.random_element(
                [
                    'https://github.com/ioet/time-tracker-backend/issues/51',
                    '#54',
                    'TT-54',
                ]
            ),
        ),
        'technologies': fields.List(
            fields.String(
                title='Technologies',
                description='List of the canonical names of the used technologies',
            ),
            required=False,
            max_items=10,
            unique=True,
            example=faker.words(
                3,
                [
                    'cosmos_db',
                    'azure',
                    'python',
                    'docker',
                    'sql',
                    'javascript',
                    'typescript',
                ],
                unique=True,
            ),
        ),
        'timezone_offset': fields.Integer(
            title='Timezone Offset',
            description='Time zone difference, in minutes, from current locale (host system settings) to UTC.',
            required=False,
            example=choice([300, -120]),
        ),
    },
)

time_entry_response_fields = {
    'running': fields.Boolean(
        readOnly=True,
        title='Is it running?',
        description='Whether this time entry is currently running or not',
        example=faker.boolean(),
    ),
    'owner_id': UUID(
        required=True,
        readOnly=True,
        title='Owner of time entry',
        description='User who owns the time entry',
        example=faker.uuid4(),
    ),
    'project_name': fields.String(
        required=True,
        title='Project Name',
        max_length=50,
        description='Name of the project where time-entry was registered',
        example=faker.word(['mobile app', 'web app']),
    ),
    'activity_name': fields.String(
        required=False,
        title='Activity Name',
        max_length=50,
        description='Name of the activity associated with the time-entry',
        example=faker.word(['development', 'QA']),
    ),
    'owner_email': fields.String(
        required=True,
        title="Owner's Email",
        max_length=50,
        description='Email of the user that owns the time-entry',
        example=faker.email(),
    ),
    'customer_id': fields.String(
        required=False,
        title='Customer ID',
        max_length=50,
        description='Unique ID for the customer the entry belongs to',
        example=faker.uuid4(),
    ),
    'customer_name': fields.String(
        required=False,
        title='Customer Name',
        max_length=50,
        description='Name of the customer the entry belongs to',
        example=faker.company(),
    ),
}
time_entry_response_fields.update(common_fields)

time_entry = ns.inherit(
    'TimeEntry',
    time_entry_input,
    time_entry_response_fields,
)

time_entries_dao = create_dao()

attributes_filter = create_attributes_filter(
    ns, time_entry, ["project_id", "activity_id", "uri"]
)

# custom attributes filter

attributes_filter.add_argument(
    'limit',
    required=False,
    type=int,
    store_missing=False,
    help="(Filter) Amount of data to return",
    location='args',
)

attributes_filter.add_argument(
    'user_id',
    required=False,
    store_missing=False,
    help="(Filter) User to filter by",
    location='args',
)

attributes_filter.add_argument(
    'month',
    required=False,
    store_missing=False,
    help="(Filter) Month to filter by",
    location='args',
)

attributes_filter.add_argument(
    'year',
    required=False,
    store_missing=False,
    help="(Filter) Year to filter by",
    location='args',
)

attributes_filter.add_argument(
    'start_date',
    required=False,
    store_missing=False,
    help="(Filter) Start to filter by",
    location='args',
)

attributes_filter.add_argument(
    'end_date',
    required=False,
    store_missing=False,
    help="(Filter) End time to filter by",
    location='args',
)

attributes_filter.add_argument(
    'timezone_offset',
    required=False,
    store_missing=False,
    help="(Filter) Time zone difference, in minutes, from current locale (host system settings) to UTC.",
    location='args',
)


@ns.route('')
class TimeEntries(Resource):
    @ns.doc('list_time_entries')
    @ns.expect(attributes_filter)
    @ns.marshal_list_with(time_entry)
    @ns.response(HTTPStatus.NOT_FOUND, 'Time entry not found')
    def get(self):
        """List all time entries"""
        conditions = attributes_filter.parse_args()
        return time_entries_dao.get_all(conditions=conditions)

    @ns.doc('create_time_entry')
    @ns.expect(time_entry_input)
    @ns.marshal_with(time_entry, code=HTTPStatus.CREATED)
    @ns.response(HTTPStatus.CONFLICT, 'There is already an active time entry')
    @ns.response(
        HTTPStatus.BAD_REQUEST,
        'Invalid format or structure of the attributes of the time entry',
    )
    @ns.response(
        HTTPStatus.UNPROCESSABLE_ENTITY,
        'This new time entry intercepts another one. '
        'Please check your start and end date.',
    )
    def post(self):
        """Create a time entry"""
        return time_entries_dao.create(ns.payload), HTTPStatus.CREATED


@ns.route('/latest')
class LatestTimeEntries(Resource):
    @ns.doc('list_latest_time_entries')
    @ns.marshal_list_with(time_entry)
    @ns.response(HTTPStatus.NOT_FOUND, 'No time entries found')
    def get(self):
        """List the latest time entries"""

        return time_entries_dao.get_lastest_entries_by_project(conditions={})


@ns.route('/featureFlags')
class featuresFlags(Resource):
    @ns.doc('flags')
    @ns.marshal_list_with(time_entry)
    @ns.response(HTTPStatus.NOT_FOUND, 'No time entries found')
    def get(self):
        """List the latest time entries"""
        featureTest = FeatureFlags("ui-list-test-users")
        test = featureTest.is_toggle_enabled_for_user()
        if test:
            return time_entries_dao.get_lastest_entries_by_project(
                conditions={}
            )
        else:
            conditions = attributes_filter.parse_args()
            return time_entries_dao.get_all(conditions=conditions)


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
    @ns.response(
        HTTPStatus.BAD_REQUEST,
        'Invalid format or structure of the attributes of the time entry',
    )
    @ns.response(
        HTTPStatus.CONFLICT,
        'A time entry already exists with this new data or there'
        ' is a bad reference for the project or activity',
    )
    @ns.expect(remove_required_constraint(time_entry_input))
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
@ns.response(
    HTTPStatus.UNPROCESSABLE_ENTITY,
    'The specified time entry is already stopped',
)
@ns.param('id', 'The unique identifier of a running time entry')
class StopTimeEntry(Resource):
    @ns.doc('stop_time_entry')
    @ns.marshal_with(time_entry)
    def post(self, id):
        """Stop a running time entry"""
        return time_entries_dao.stop(id)


@ns.route('/<string:id>/restart')
@ns.response(HTTPStatus.NOT_FOUND, 'Stopped time entry not found')
@ns.response(
    HTTPStatus.UNPROCESSABLE_ENTITY,
    'The specified time entry is already running',
)
@ns.param('id', 'The unique identifier of a stopped time entry')
class RestartTimeEntry(Resource):
    @ns.doc('restart_time_entry')
    @ns.marshal_with(time_entry)
    def post(self, id):
        """Restart a time entry"""
        return time_entries_dao.restart(id)


@ns.route('/running')
@ns.response(HTTPStatus.OK, 'The time entry that is active: currently running')
@ns.response(HTTPStatus.NOT_FOUND, 'There is no time entry running right now')
class ActiveTimeEntry(Resource):
    @ns.doc('running_time_entry')
    @ns.marshal_with(time_entry)
    def get(self):
        """Find the time entry that is running"""
        return time_entries_dao.find_running()


summary_attribs_parser = ns.parser()
summary_attribs_parser.add_argument(
    'time_offset',
    required=False,
    type=int,
    store_missing=False,
    help="(Filter) Time zone difference, in minutes, from current locale (host system settings) to UTC.",
    location='args',
)


@ns.route('/summary')
@ns.response(HTTPStatus.OK, 'Summary of worked time in the current month')
@ns.response(
    HTTPStatus.NOT_FOUND, 'There is no time entry in the current month'
)
class WorkedTimeSummary(Resource):
    @ns.expect(summary_attribs_parser)
    @ns.doc('summary_of_worked_time')
    def get(self):
        """Find the summary of worked time"""
        conditions = summary_attribs_parser.parse_args()
        return time_entries_dao.get_worked_time(conditions)


time_entry_paginated = ns.model(
    'TimeEntryPaginated',
    {
        'records_total': fields.Integer(
            title='Records total',
            description='Total number of entries.',
        ),
        'data': fields.List(fields.Nested(time_entry)),
    },
)

paginated_attribs_parser = ns.parser()
paginated_attribs_parser.add_argument(
    'length',
    required=True,
    type=int,
    help="(Filter) The number of rows the endpoint should return.",
    location='args',
)

paginated_attribs_parser.add_argument(
    'start',
    required=True,
    type=int,
    help="(Filter) The number of rows to be removed from the query. (aka offset)",
    location='args',
)

paginated_attribs_parser.add_argument(
    'user_id',
    required=False,
    store_missing=False,
    help="(Filter) User to filter by",
    location='args',
)

paginated_attribs_parser.add_argument(
    'month',
    required=False,
    store_missing=False,
    help="(Filter) Month to filter by",
    location='args',
)

paginated_attribs_parser.add_argument(
    'year',
    required=False,
    store_missing=False,
    help="(Filter) Year to filter by",
    location='args',
)

paginated_attribs_parser.add_argument(
    'start_date',
    required=True,
    store_missing=False,
    help="(Filter) Start to filter by",
    location='args',
)

paginated_attribs_parser.add_argument(
    'end_date',
    required=True,
    store_missing=False,
    help="(Filter) End time to filter by",
    location='args',
)

paginated_attribs_parser.add_argument(
    'timezone_offset',
    required=False,
    store_missing=False,
    help="(Filter) Time zone difference, in minutes, from current locale (host system settings) to UTC.",
    location='args',
)


@ns.route('/paginated')
@ns.response(HTTPStatus.OK, 'Time Entries paginated')
@ns.response(HTTPStatus.NOT_FOUND, 'Time entry not found')
class PaginatedTimeEntry(Resource):
    @ns.expect(paginated_attribs_parser)
    @ns.doc('list_time_entries_paginated')
    @ns.marshal_list_with(time_entry_paginated)
    def get(self):
        """List all time entries paginated"""
        conditions = paginated_attribs_parser.parse_args()
        return time_entries_dao.get_all_paginated(conditions)
