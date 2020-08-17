from faker import Faker
from flask_restplus import fields, Resource
from flask_restplus._http import HTTPStatus

from time_tracker_api.technologies.technologies_model import create_dao
from time_tracker_api.api import (
    common_fields,
    api,
    remove_required_constraint,
    NullableString,
    UUID,
)


faker = Faker()

ns = api.namespace(
    'technologies', description='Namespace of the API for technologies'
)

# technology Model
technology_input = ns.model(
    'TechnologyInput',
    {
        'name': fields.String(
            required=True,
            title='Name',
            max_length=50,
            description='Canonical name of the technology',
            example=faker.word(['python', 'postgraphile', 'neo4j']),
        ),
        'first_use_time_entry_id': UUID(
            required=True,
            title='First use time entry identifier',
            description='Time entry where this technology was used for the first time',
            example=faker.uuid4(),
        ),
        'creation_date': fields.String(
            title='Creation date',
            required=False,
            description='Creation date of the technology',
            example='2020-04-01T05:00:00+00:00',
        ),
    },
)

technology_response_fields = {}
technology_response_fields.update(common_fields)

technology = ns.inherit(
    'Technology', technology_input, technology_response_fields
)

technology_dao = create_dao()


@ns.route('')
class Technologies(Resource):
    @ns.doc('list_technologies')
    @ns.marshal_list_with(technology)
    def get(self):
        """List all technologies"""
        return technology_dao.get_all()

    @ns.doc('create_technology')
    @ns.response(HTTPStatus.CONFLICT, 'This technology already exists')
    @ns.response(
        HTTPStatus.BAD_REQUEST,
        'Invalid format or structure of the attributes of the technology',
    )
    @ns.expect(technology_input)
    @ns.marshal_with(technology, code=HTTPStatus.CREATED)
    def post(self):
        """Create a technology"""
        return technology_dao.create(ns.payload), HTTPStatus.CREATED


@ns.route('/<string:id>')
@ns.response(HTTPStatus.NOT_FOUND, 'technology not found')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
@ns.param('id', 'The technology identifier')
class Technology(Resource):
    @ns.doc('get_technology')
    @ns.marshal_with(technology)
    def get(self, id):
        """Get a technology"""
        return technology_dao.get(id)

    @ns.doc('update_technology')
    @ns.expect(remove_required_constraint(technology_input))
    @ns.response(
        HTTPStatus.BAD_REQUEST, 'Invalid format or structure of the technology'
    )
    @ns.response(
        HTTPStatus.CONFLICT, 'An technology already exists with this data'
    )
    @ns.marshal_with(technology)
    def put(self, id):
        """Update a technology"""
        return technology_dao.update(id, ns.payload)

    @ns.doc('delete_technology')
    @ns.response(HTTPStatus.NO_CONTENT, 'technology deleted successfully')
    def delete(self, id):
        """Delete a technology"""
        technology_dao.delete(id)
        return None, HTTPStatus.NO_CONTENT
