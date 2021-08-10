from unittest.mock import ANY

from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

from utils.enums.status import Status

fake = Faker()

valid_customer_data = {
    "name": fake.company(),
    "description": fake.paragraph(),
    "tenant_id": fake.uuid4(),
}

fake_customer = (
    {
        "id": fake.random_int(1, 9999),
    }
).update(valid_customer_data)


def test_create_customer_should_succeed_with_valid_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao

    repository_create_mock = mocker.patch.object(
        customer_dao.repository, 'create', return_value=fake_customer
    )

    response = client.post(
        "/customers",
        headers=valid_header,
        json=valid_customer_data,
        follow_redirects=True,
    )

    assert HTTPStatus.CREATED == response.status_code
    repository_create_mock.assert_called_once()


def test_create_customer_should_reject_bad_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao

    repository_create_mock = mocker.patch.object(
        customer_dao.repository, 'create', return_value=fake_customer
    )

    response = client.post(
        "/customers", headers=valid_header, json=None, follow_redirects=True
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_create_mock.assert_not_called()


def test_list_all_customers(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao

    repository_find_all_mock = mocker.patch.object(
        customer_dao.repository, 'find_all', return_value=[]
    )

    response = client.get(
        "/customers", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    json_data = json.loads(response.data)
    assert [] == json_data
    repository_find_all_mock.assert_called_once()


def test_get_customer_should_succeed_with_valid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao

    valid_id = fake.uuid4()

    repository_find_mock = mocker.patch.object(
        customer_dao.repository, 'find', return_value=fake_customer
    )

    response = client.get(
        "/customers/%s" % valid_id, headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    fake_customer == json.loads(response.data)
    repository_find_mock.assert_called_once_with(str(valid_id), ANY)


def test_get_customer_should_return_not_found_with_invalid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_find_mock = mocker.patch.object(
        customer_dao.repository, 'find', side_effect=NotFound
    )

    response = client.get(
        "/customers/%s" % invalid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id), ANY)


def test_get_customer_should_return_422_for_invalid_id_format(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_find_mock = mocker.patch.object(
        customer_dao.repository, 'find', side_effect=UnprocessableEntity
    )

    response = client.get(
        "/customers/%s" % invalid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id), ANY)


def test_update_customer_should_succeed_with_valid_data(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao

    repository_update_mock = mocker.patch.object(
        customer_dao.repository, 'partial_update', return_value=fake_customer
    )

    valid_id = fake.random_int(1, 9999)
    response = client.put(
        "/customers/%s" % valid_id,
        headers=valid_header,
        json=valid_customer_data,
        follow_redirects=True,
    )

    assert HTTPStatus.OK == response.status_code
    fake_customer == json.loads(response.data)
    repository_update_mock.assert_called_once_with(
        str(valid_id), valid_customer_data, ANY
    )


def test_update_customer_should_reject_bad_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao

    repository_update_mock = mocker.patch.object(
        customer_dao.repository, 'partial_update', return_value=fake_customer
    )

    valid_id = fake.random_int(1, 9999)
    response = client.put(
        "/customers/%s" % valid_id,
        headers=valid_header,
        json=None,
        follow_redirects=True,
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_update_mock.assert_not_called()


def test_update_customer_should_return_not_found_with_invalid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_update_mock = mocker.patch.object(
        customer_dao.repository, 'partial_update', side_effect=NotFound
    )

    response = client.put(
        "/customers/%s" % invalid_id,
        headers=valid_header,
        json=valid_customer_data,
        follow_redirects=True,
    )

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(
        str(invalid_id), valid_customer_data, ANY
    )


def test_delete_customer_should_succeed_with_valid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao

    valid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(
        customer_dao.repository, 'partial_update', return_value=None
    )

    response = client.delete(
        "/customers/%s" % valid_id, headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    repository_remove_mock.assert_called_once_with(
        str(valid_id), {'status': Status.INACTIVE.value}, ANY
    )


def test_delete_customer_should_return_not_found_with_invalid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(
        customer_dao.repository, 'partial_update', side_effect=NotFound
    )

    response = client.delete(
        "/customers/%s" % invalid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_remove_mock.assert_called_once_with(
        str(invalid_id), {'status': Status.INACTIVE.value}, ANY
    )


def test_delete_customer_should_return_422_for_invalid_id_format(
    client: FlaskClient,
    mocker: MockFixture,
    tenant_id: str,
    valid_header: dict,
):
    from time_tracker_api.customers.customers_namespace import customer_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_remove_mock = mocker.patch.object(
        customer_dao.repository,
        'partial_update',
        side_effect=UnprocessableEntity,
    )

    response = client.delete(
        "/customers/%s" % invalid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_remove_mock.assert_called_once_with(
        str(invalid_id), {'status': Status.INACTIVE.value}, ANY
    )


def test_list_all_active_customers(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.customers.customers_namespace import customer_dao

    repository_find_all_mock = mocker.patch.object(
        customer_dao.repository, 'find_all', return_value=[]
    )

    response = client.get(
        "/customers", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    json_data = json.loads(response.data)
    assert [] == json_data

    repository_find_all_mock.assert_called_once_with(ANY, conditions={})


# def test_list_only_active_customers(
#     client: FlaskClient, mocker: MockFixture, valid_header: dict
# ):
#     from time_tracker_api.customers.customers_namespace import customer_dao

#     repository_find_all_mock = mocker.patch.object(
#         customer_dao.repository, 'find_all', return_value=[]
#     )

#     response = client.get(
#         "/customers?status=active",
#         headers=valid_header,
#         follow_redirects=True,
# )
