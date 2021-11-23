import pytest
import json
from faker import Faker

import azure.functions as func

import time_tracker.customers._application._customers as azure_customers
from time_tracker._infrastructure import DB
from time_tracker.customers import _domain as domain_customers
from time_tracker.customers import _infrastructure as infrastructure_customers


CUSTOMER_URL = "/api/customers/"


def test__customer_azure_endpoint__creates_a_customer__when_customer_has_all_necesary_attributes(
    customer_factory
):
    customer_body = customer_factory().__dict__

    body = json.dumps(customer_body).encode("utf-8")
    req = func.HttpRequest(
        method='POST',
        body=body,
        url=CUSTOMER_URL,
    )

    response = azure_customers._create_customer.create_customer(req)
    customer_json_data = json.loads(response.get_body())
    customer_body['id'] = customer_json_data['id']

    assert response.status_code == 201
    assert customer_json_data == customer_body


def test__customer_azure_endpoint__returns_a_status_400__when_dont_recieve_all_necessary_attributes():
    customer_to_insert = {
        "id": None,
        "name": Faker().user_name(),
        "deleted": False,
        "status": 1
    }

    body = json.dumps(customer_to_insert).encode("utf-8")
    req = func.HttpRequest(
        method='POST',
        body=body,
        url=CUSTOMER_URL,
    )

    response = azure_customers._create_customer.create_customer(req)

    assert response.status_code == 400
    assert response.get_body() == b'Invalid format or structure of the attributes of the customer'
