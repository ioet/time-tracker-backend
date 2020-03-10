from flask_restplus import fields, Resource, Namespace

ns = Namespace('time_entries', description='API for time entries')

# TimeEntry Model
time_entry = ns.model('TimeEntry', {
    'id': fields.String(readOnly=True,
                        required=True,
                        title='Identifier',
                        description='The unique id of the time entry'),
    'project_id': fields.String(required=True,
                                title='Project',
                                max_length=64,
                                description='The id of the selected project'),
    'activity_id': fields.String(required=False,
                                 title='Activity',
                                 max_length=64,
                                 description='The id of the selected activity'),
    'technologies': fields.String(required=True,
                                  title='Technologies',
                                  max_length=64,
                                  description='Canonical names of the used technologies during this period'),
    'description': fields.String(title='Comments',
                                 description='Comments about the time entry'),
    'start_date': fields.DateTime(required=True,
                                  title='Start date',
                                  description='When the user started doing this activity'),
    'end_date': fields.DateTime(required=True,
                                title='End date',
                                description='When the user ended doing this activity'),

    'user_id': fields.String(required=True,
                             title='Tenant',
                             max_length=64,
                             description='The user who created this time entry'),
    'tenant_id': fields.String(required=True,
                               title='Tenant',
                               max_length=64,
                               description='The tenant this time entry belongs to'),
})

time_entry_response = ns.inherit('TimeEntryResponse', time_entry, {
    'running': fields.Boolean(title='Is it running?',
                              description='Whether this time entry is currently running '
                                          'or not'),
})


@ns.route('/')
class TimeEntries(Resource):
    @ns.doc('list_time_entries')
    @ns.marshal_list_with(time_entry_response, code=200)
    def get(self):
        """List all available time entries"""
        return []

    @ns.doc('create_time_entry')
    @ns.expect(time_entry)
    @ns.marshal_with(time_entry_response, code=201)
    @ns.response(400, 'Invalid format of the attributes of the time entry')
    def post(self):
        """Starts a time entry by creating it"""
        return ns.payload, 201


@ns.route('/<string:id>')
@ns.response(404, 'Time entry not found')
@ns.param('id', 'The unique identifier of the time entry')
class TimeEntry(Resource):
    @ns.doc('get_time_entry')
    @ns.marshal_with(time_entry_response)
    def get(self, id):
        """Retrieve all the data of a single time entry"""
        return {}

    @ns.doc('delete_time_entry')
    @ns.response(204, 'The time entry was deleted successfully (No content is returned)')
    def delete(self, id):
        """Deletes a time entry"""
        return None, 204

    @ns.doc('put_time_entry')
    @ns.response(400, 'Invalid format of the attributes of the time entry.')
    @ns.expect(time_entry)
    @ns.marshal_with(time_entry_response)
    def put(self, id):
        """Updates a time entry"""
        return ns.payload


@ns.route('/stop/<string:id>')
@ns.response(404, 'Running time entry not found')
@ns.param('id', 'The unique identifier of a running time entry')
class StopTimeEntry(Resource):
    @ns.doc('stop_time_entry')
    @ns.response(204, 'The time entry was stopped successfully (No content is returned)')
    def post(self, id):
        """Stops a running time entry"""
        return None, 204


@ns.route('/continue/<string:id>')
@ns.response(404, 'Stopped time entry not found')
@ns.param('id', 'The unique identifier of a stopped time entry')
class ContinueTimeEntry(Resource):
    @ns.doc('continue_time_entry')
    @ns.response(204, 'The time entry was continued successfully (No content is returned)')
    def post(self, id):
        """Restart an stopped time entry"""
        return None, 204
