from unittest.mock import ANY, Mock

from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

from utils.azure_users import AzureConnection


def test_users_response_contains_expected_props(
    client: FlaskClient,
    valid_header: dict,
):

    AzureConnection.users = Mock(
        return_value=[{'name': 'dummy', 'email': 'dummy', 'role': 'dummy'}]
    )

    response = client.get(
        '/users',
        headers=valid_header,
    )

    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)[0]
    assert 'email' in json.loads(response.data)[0]
    assert 'role' in json.loads(response.data)[0]
