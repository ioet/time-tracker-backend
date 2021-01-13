from unittest.mock import Mock, patch
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from utils.azure_users import AzureConnection
from pytest import mark


def test_users_response_contains_expected_props(
    client: FlaskClient, valid_header: dict,
):

    AzureConnection.users = Mock(
        return_value=[{'name': 'dummy', 'email': 'dummy', 'role': 'dummy'}]
    )

    response = client.get('/users', headers=valid_header,)

    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)[0]
    assert 'email' in json.loads(response.data)[0]
    assert 'role' in json.loads(response.data)[0]


def test_update_user_role_response_contains_expected_props(
    client: FlaskClient, valid_header: dict, user_id: str,
):
    valid_user_role_data = {'role': 'admin'}
    AzureConnection.update_user_role = Mock(
        return_value={'name': 'dummy', 'email': 'dummy', 'role': 'dummy'}
    )

    response = client.post(
        f'/users/{user_id}/roles',
        headers=valid_header,
        json=valid_user_role_data,
    )

    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)
    assert 'email' in json.loads(response.data)
    assert 'role' in json.loads(response.data)


@mark.parametrize(
    'role_id,action', [('test', 'grant'), ('admin', 'revoke')],
)
def test_update_role_response_contains_expected_props(
    client: FlaskClient, valid_header: dict, user_id: str, role_id, action
):
    AzureConnection.update_role = Mock(
        return_value={'name': 'dummy', 'email': 'dummy', 'roles': []}
    )
    response = client.post(
        f'/users/{user_id}/roles/{role_id}/{action}', headers=valid_header,
    )
    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)
    assert 'email' in json.loads(response.data)
    assert 'roles' in json.loads(response.data)


@patch('utils.azure_users.AzureConnection.update_user_role', new_callable=Mock)
def test_on_post_update_user_role_is_being_called_with_valid_arguments(
    update_user_role_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
):

    valid_user_role_data = {'role': 'admin'}
    response = client.post(
        f'/users/{user_id}/roles',
        headers=valid_header,
        json=valid_user_role_data,
    )

    assert HTTPStatus.OK == response.status_code
    update_user_role_mock.assert_called_once_with(
        user_id, valid_user_role_data['role']
    )


@patch('utils.azure_users.AzureConnection.update_user_role', new_callable=Mock)
def test_on_delete_update_user_role_is_being_called_with_valid_arguments(
    update_user_role_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
):

    response = client.delete(
        f'/users/{user_id}/roles/time-tracker-admin', headers=valid_header,
    )

    assert HTTPStatus.OK == response.status_code
    update_user_role_mock.assert_called_once_with(user_id, role=None)


@patch('utils.azure_users.AzureConnection.update_role', new_callable=Mock)
@mark.parametrize(
    'role_id,action,is_grant',
    [
        ('admin', 'grant', True),
        ('admin', 'revoke', False),
        ('test', 'grant', True),
        ('test', 'revoke', False),
    ],
)
def test_update_role_is_called_properly_on_each_action(
    update_role_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
    role_id,
    action,
    is_grant,
):
    response = client.post(
        f'/users/{user_id}/roles/{role_id}/{action}', headers=valid_header,
    )

    assert HTTPStatus.OK == response.status_code
    update_role_mock.assert_called_once_with(
        user_id, role_id, is_grant=is_grant
    )
