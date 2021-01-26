from unittest.mock import Mock, patch
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from utils.azure_users import AzureConnection
from pytest import mark


@patch('msal.ConfidentialClientApplication', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch(
    'utils.azure_users.AzureConnection.is_test_user', Mock(return_value=True)
)
@patch('utils.azure_users.AzureConnection.users_v2')
def test_users_response_contains_expected_props(
    users_v2_mock, client: FlaskClient, valid_header: dict,
):
    users_v2_mock.return_value = [
        {'name': 'dummy', 'email': 'dummy', 'roles': ['dummy-role']}
    ]
    response = client.get('/users', headers=valid_header)

    users_v2_mock.assert_called()
    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)[0]
    assert 'email' in json.loads(response.data)[0]
    assert 'roles' in json.loads(response.data)[0]
    assert ['dummy-role'] == json.loads(response.data)[0]['roles']


@patch('utils.azure_users.AzureConnection.update_role')
@mark.parametrize(
    'role_id,action', [('test', 'grant'), ('admin', 'revoke')],
)
def test_update_role_response_contains_expected_props(
    update_role_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
    role_id,
    action,
):
    update_role_mock.return_value = {
        'name': 'dummy',
        'email': 'dummy',
        'roles': [],
    }
    response = client.post(
        f'/users/{user_id}/roles/{role_id}/{action}', headers=valid_header,
    )
    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)
    assert 'email' in json.loads(response.data)
    assert 'roles' in json.loads(response.data)


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
    update_role_mock.return_value = {}
    response = client.post(
        f'/users/{user_id}/roles/{role_id}/{action}', headers=valid_header,
    )

    assert HTTPStatus.OK == response.status_code
    update_role_mock.assert_called_once_with(
        user_id, role_id, is_grant=is_grant
    )
