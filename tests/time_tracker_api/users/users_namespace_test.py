from unittest.mock import Mock, patch
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
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


def test_update_user_role_response_contains_expected_props(
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
):
    valid_user_role_data = {'role': 'admin'}
    AzureConnection.update_user_role = Mock(
        return_value={'name': 'dummy', 'email': 'dummy', 'role': 'dummy'}
    )

    response = client.put(
        f'/users/{user_id}', headers=valid_header, json=valid_user_role_data
    )

    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)
    assert 'email' in json.loads(response.data)
    assert 'role' in json.loads(response.data)


@patch('utils.azure_users.AzureConnection.update_user_role', new_callable=Mock)
def test_update_user_role_is_being_called_with_valid_arguments(
    update_user_role_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
):

    valid_user_role_data = {'role': 'admin'}
    response = client.put(
        f'/users/{user_id}', headers=valid_header, json=valid_user_role_data
    )

    assert HTTPStatus.OK == response.status_code
    update_user_role_mock.assert_called_once_with(
        user_id, valid_user_role_data['role']
    )