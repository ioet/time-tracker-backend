from faker import Faker
from flask_restplus import Namespace, Resource, fields
from flask_restplus._http import HTTPStatus
from flask import request

from time_tracker_api.api import common_fields
from time_tracker_api.customers.customers_model import create_dao

faker = Faker()

ns = Namespace('customers', description='API for customers')

# Customer Model
customer_input = ns.model('CustomerInput', {
    'name': fields.String(
        title='Name',
        required=True,
        max_length=50,
        description='Name of the customer',
        example=faker.company(),
    ),
    'description': fields.String(
        title='Description',
        required=False,
        max_length=250,
        description='Description about the customer',
        example=faker.paragraph(),
    ),
})

customer_response_fields = {}
customer_response_fields.update(common_fields)

customer = ns.inherit(
    'Customer',
    customer_input,
    customer_response_fields
)

customer_dao = create_dao()


@ns.route('')
class Customers(Resource):
    @ns.doc('list_customers')
    @ns.marshal_list_with(customer)
    def get(self):
        """List all customers"""
        return customer_dao.get_all(conditions=request.args)

    @ns.doc('create_customer')
    @ns.response(HTTPStatus.CONFLICT, 'This customer already exists')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid format or structure '
                                         'of the attributes of the customer')
    @ns.expect(customer_input)
    @ns.marshal_with(customer, code=HTTPStatus.CREATED)
    def post(self):
        """Create a customer"""
        return customer_dao.create(ns.payload), HTTPStatus.CREATED


@ns.route('/<string:id>')
@ns.response(HTTPStatus.NOT_FOUND, 'This customer does not exist')
@ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The data has an invalid format')
@ns.param('id', 'The customer identifier')
class Customer(Resource):
    @ns.doc('get_customer')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'The id has an invalid format')
    @ns.marshal_with(customer)
    def get(self, id):
        """Get a customer"""
        return customer_dao.get(id)

    @ns.doc('update_customer')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Invalid format or structure '
                                         'of the attributes of the customer')
    @ns.response(HTTPStatus.CONFLICT, 'A customer already exists with this new data')
    @ns.expect(customer_input)
    @ns.marshal_with(customer)
    def put(self, id):
        """Update a customer"""
        return customer_dao.update(id, ns.payload)

    @ns.doc('delete_customer')
    @ns.response(HTTPStatus.NO_CONTENT, 'Customer successfully deleted')
    def delete(self, id):
        """Delete a customer"""
        customer_dao.delete(id)
        return None, HTTPStatus.NO_CONTENT
