from http import HTTPStatus
import json
from faker import Faker

import azure.functions as func

import time_tracker.customers._application._customers as azure_customers

CUSTOMER_URL = "/api/customers/"


def test__create_customer_azure_endpoint__creates_a_customer__when_customer_has_all_necesary_attributes(
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

    assert response.status_code == HTTPStatus.CREATED
    assert customer_json_data == customer_body


def test__create_customer_azure_endpoint__returns_a_status_400__when_dont_recieve_all_necessary_attributes():
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

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b'Invalid format or structure of the attributes of the customer'


def test__delete_customer_azure_endpoint__returns_a_customer_with_true_deleted__when_its_id_is_found(
    test_db, customer_factory, insert_customer
):
    customer_preinsert = customer_factory()
    inserted_customer = insert_customer(customer_preinsert, test_db).__dict__

    req = func.HttpRequest(
        method='DELETE',
        body=None,
        url=CUSTOMER_URL,
        route_params={"id": inserted_customer["id"]},
    )

    response = azure_customers._delete_customer.delete_customer(req)
    customer_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == HTTPStatus.OK
    assert customer_json_data['deleted'] is True


def test__delete_customer_azure_endpoint__returns_not_found__when_its_id_is_not_found():
    req = func.HttpRequest(
        method='DELETE',
        body=None,
        url=CUSTOMER_URL,
        route_params={"id": Faker().pyint()},
    )

    response = azure_customers._delete_customer.delete_customer(req)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.get_body() == b'Not found'


def test__update_customer_azure_endpoint__returns_an_updated_customer__when_customer_has_all_necesary_attributes(
    test_db, customer_factory, insert_customer
):
    existent_customer = customer_factory()
    inserted_customer = insert_customer(existent_customer, test_db).__dict__

    inserted_customer["description"] = Faker().sentence()

    body = json.dumps(inserted_customer).encode("utf-8")
    req = func.HttpRequest(
        method='PUT',
        body=body,
        url=CUSTOMER_URL,
        route_params={"id": inserted_customer["id"]},
    )

    response = azure_customers._update_customer.update_customer(req)
    customer_json_data = json.loads(response.get_body())

    assert response.status_code == HTTPStatus.OK
    assert customer_json_data == inserted_customer


def test__update_customer_azure_endpoint__returns_update_a_customer__when_customer_has_all_necesary_attributes(
    customer_factory
):
    existent_customer = customer_factory().__dict__

    body = json.dumps(existent_customer).encode("utf-8")
    req = func.HttpRequest(
        method='PUT',
        body=body,
        url=CUSTOMER_URL,
        route_params={"id": Faker().pyint()},
    )

    response = azure_customers._update_customer.update_customer(req)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.get_body() == b'This customer does not exist or is duplicated'


def test__update_customer_azure_endpoint__returns_invalid_format__when_customer_doesnt_have_all_necesary_attributes(
    customer_factory, insert_customer, test_db
):
    existent_customer = customer_factory()
    inserted_customer = insert_customer(existent_customer, test_db).__dict__

    inserted_customer.pop("name")

    body = json.dumps(inserted_customer).encode("utf-8")
    req = func.HttpRequest(
        method='PUT',
        body=body,
        url=CUSTOMER_URL,
        route_params={"id": inserted_customer["id"]},
    )

    response = azure_customers._update_customer.update_customer(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b'Invalid format or structure of the attributes of the customer'


def test__delete_customers_azure_endpoint__returns_a_status_code_400__when_customer_recive_invalid_id(
):
    req = func.HttpRequest(
        method="DELETE",
        body=None,
        url=CUSTOMER_URL,
        route_params={"id": "invalid id"},
    )

    response = azure_customers._delete_customer.delete_customer(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b'Invalid Format ID'


def test__customers_azure_endpoint__returns_all_customers(
    test_db, customer_factory, insert_customer
):
    customer_to_insert = customer_factory()

    inserted_customer = insert_customer(customer_to_insert, test_db).__dict__

    req = func.HttpRequest(method='GET', body=None, url=CUSTOMER_URL)
    response = azure_customers._get_customers.get_customers(req)
    customers_json_data = response.get_body().decode("utf-8")
    customer_list = json.loads(customers_json_data)

    assert response.status_code == HTTPStatus.OK
    assert customers_json_data <= json.dumps(inserted_customer)
    assert customer_list.pop() == inserted_customer


def test__customer_azure_endpoint__returns_a_customer__when_customer_matches_its_id(
    test_db, customer_factory, insert_customer
):
    existent_customer = customer_factory()
    inserted_customer = insert_customer(existent_customer, test_db).__dict__

    req = func.HttpRequest(
        method='GET',
        body=None,
        url=CUSTOMER_URL,
        route_params={"id": inserted_customer["id"]},
    )

    response = azure_customers._get_customers.get_customers(req)
    customer_json_data = response.get_body().decode("utf-8")

    assert response.status_code == HTTPStatus.OK
    assert customer_json_data == json.dumps(inserted_customer)


def test__customer_azure_endpoint__returns_invalid_id__when_customer_not_matches_its_id():
    req = func.HttpRequest(
        method='GET',
        body=None,
        url=CUSTOMER_URL,
        route_params={"id": "Invalid ID"},
    )

    response = azure_customers._get_customers.get_customers(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b'The id has an invalid format'
