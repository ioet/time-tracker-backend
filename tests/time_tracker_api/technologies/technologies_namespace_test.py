from unittest.mock import ANY, Mock

import pytest

from faker import Faker
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus

from werkzeug.exceptions import NotFound, UnprocessableEntity, HTTPException


@pytest.fixture
def technology_dao():
    from time_tracker_api.technologies.technologies_namespace import (
        technology_dao,
    )

    return technology_dao


def test_list_all_technologies(
    client: FlaskClient, valid_header: dict, technology_dao
):
    technology_dao.repository.find_all = Mock(return_value=[])
    response = client.get("/technologies", headers=valid_header)
    assert HTTPStatus.OK == response.status_code


def test_get_technology_suceeds_with_valid_id(
    client: FlaskClient, valid_header: dict, technology_dao
):
    technology_dao.repository.find = Mock(return_value={})
    id: str = Faker().uuid4()

    response = client.get(f"/technologies/{id}", headers=valid_header)

    assert HTTPStatus.OK == response.status_code
    technology_dao.repository.find.assert_called_once_with(id, ANY)


def test_create_technology_suceeds_with_valid_input(
    client: FlaskClient, valid_header: dict, technology_dao
):
    technology_dao.repository.create = Mock(return_value={})
    payload = {
        'name': 'neo4j',
        'creation_date': '2020-04-01T05:00:00+00:00',
        'first_use_time_entry_id': Faker().uuid4(),
    }

    response = client.post("/technologies", headers=valid_header, json=payload)

    assert HTTPStatus.CREATED == response.status_code
    technology_dao.repository.create.assert_called_once()


def test_create_technology_fails_with_invalid_input(
    client: FlaskClient, valid_header: dict, technology_dao
):
    technology_dao.repository.create = Mock(return_value={})

    response = client.post("/technologies", headers=valid_header, json={})

    assert HTTPStatus.BAD_REQUEST == response.status_code
    technology_dao.repository.create.assert_not_called()


def test_update_technology_succeeds_with_valid_input(
    client: FlaskClient, valid_header: dict, technology_dao
):

    technology_dao.repository.partial_update = Mock({})
    id: str = Faker().uuid4()
    payload = {
        'name': 'neo4j',
        'creation_date': '2020-04-01T05:00:00+00:00',
        'first_use_time_entry_id': Faker().uuid4(),
    }

    response = client.put(
        f"/technologies/{id}", headers=valid_header, json=payload
    )

    assert HTTPStatus.OK == response.status_code
    technology_dao.repository.partial_update.assert_called_once_with(
        id, payload, ANY
    )


def test_update_technology_fails_with_invalid_input(
    client: FlaskClient, valid_header: dict, technology_dao
):

    technology_dao.repository.partial_update = Mock({})
    id: str = Faker().uuid4()

    response = client.put(
        f"/technologies/{id}", headers=valid_header, json=None
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    technology_dao.repository.partial_update.assert_not_called()


def test_delete_technology_suceeds(
    client: FlaskClient, valid_header: dict, technology_dao
):
    technology_dao.repository.delete = Mock(None)
    id: str = Faker().uuid4()

    response = client.delete(f'/technologies/{id}', headers=valid_header)

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    technology_dao.repository.delete.assert_called_once_with(id, ANY)


@pytest.mark.parametrize(
    'http_exception,http_status',
    [
        (NotFound, HTTPStatus.NOT_FOUND),
        (UnprocessableEntity, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
def test_get_technology_raise_http_exception_on_error(
    client: FlaskClient,
    valid_header: dict,
    http_exception: HTTPException,
    http_status: tuple,
    technology_dao,
):

    technology_dao.repository.find = Mock(side_effect=http_exception)
    id: str = Faker().uuid4()

    response = client.get(f"/technologies/{id}", headers=valid_header)

    assert http_status == response.status_code
    technology_dao.repository.find.assert_called_once_with(id, ANY)


@pytest.mark.parametrize(
    'http_exception,http_status',
    [
        (NotFound, HTTPStatus.NOT_FOUND),
        (UnprocessableEntity, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
def test_delete_technology_raise_http_exception_on_error(
    client: FlaskClient,
    valid_header: dict,
    http_exception: HTTPException,
    http_status: tuple,
    technology_dao,
):

    technology_dao.repository.delete = Mock(side_effect=http_exception)
    id: str = Faker().uuid4()

    response = client.delete(f"/technologies/{id}", headers=valid_header)

    assert http_status == response.status_code
    technology_dao.repository.delete.assert_called_once_with(id, ANY)


@pytest.mark.parametrize(
    'http_exception,http_status',
    [
        (NotFound, HTTPStatus.NOT_FOUND),
        (UnprocessableEntity, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
def test_update_technology_raise_http_exception_on_error(
    client: FlaskClient,
    valid_header: dict,
    http_exception: HTTPException,
    http_status: tuple,
    technology_dao,
):

    technology_dao.repository.partial_update = Mock(side_effect=http_exception)
    id: str = Faker().uuid4()
    payload = {}

    response = client.put(
        f"/technologies/{id}", headers=valid_header, json=payload
    )

    assert http_status == response.status_code
    technology_dao.repository.partial_update.assert_called_once_with(
        id, payload, ANY
    )
