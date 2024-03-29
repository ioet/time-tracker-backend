from unittest.mock import Mock, patch
from flask import json
from faker import Faker
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest import mark


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.get_user')
def test_get_user_response_contains_expected_props(
    get_user_mock, client: FlaskClient, valid_header: dict,
):
    get_user_mock.return_value = {
        'name': 'dummy',
        'email': 'dummy',
        'roles': ['dummy-role'],
        'groups': ['dummy-group'],
    }
    user_id = (Faker().uuid4(),)
    response = client.get(f'/users/{user_id}', headers=valid_header)

    get_user_mock.assert_called()
    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)
    assert 'email' in json.loads(response.data)
    assert 'roles' in json.loads(response.data)
    assert 'groups' in json.loads(response.data)
    assert ['dummy-role'] == json.loads(response.data)['roles']
    assert ['dummy-group'] == json.loads(response.data)['groups']


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch(
    'utils.azure_users.AzureConnection.is_test_user', Mock(return_value=True)
)
@patch('utils.azure_users.AzureConnection.users')
def test_users_response_contains_expected_props(
    users_mock, client: FlaskClient, valid_header: dict,
):
    users_mock.return_value = [
        {
            'name': 'dummy',
            'email': 'dummy',
            'roles': ['dummy-role'],
            'groups': ['dummy-group'],
        }
    ]
    response = client.get('/users', headers=valid_header)

    users_mock.assert_called()
    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)[0]
    assert 'email' in json.loads(response.data)[0]
    assert 'roles' in json.loads(response.data)[0]
    assert 'groups' in json.loads(response.data)[0]
    assert ['dummy-role'] == json.loads(response.data)[0]['roles']
    assert ['dummy-group'] == json.loads(response.data)[0]['groups']


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
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
        'groups': [],
    }
    response = client.post(
        f'/users/{user_id}/roles/{role_id}/{action}', headers=valid_header,
    )
    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)
    assert 'email' in json.loads(response.data)
    assert 'roles' in json.loads(response.data)
    assert 'groups' in json.loads(response.data)


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
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


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.is_user_in_group')
@mark.parametrize(
    'group_name, expected_value', [('admin', True), ('admin', False)]
)
def test_if_user_is_in_group(
    is_user_in_group_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
    group_name,
    expected_value,
):
    is_user_in_group_mock.return_value = {'value': expected_value}
    valid_data = {'group_name': group_name}

    response = client.post(
        f'/users/{user_id}/is-member-of', headers=valid_header, json=valid_data
    )
    assert HTTPStatus.OK == response.status_code
    assert 'value' in json.loads(response.data)


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.add_user_to_group')
def test_add_to_group(
    add_user_to_group_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
):

    add_user_to_group_mock.return_value = {}
    valid_data = {'group_name': 'dummy_group'}

    response = client.post(
        f'/users/{user_id}/groups/add', headers=valid_header, json=valid_data
    )
    assert HTTPStatus.OK == response.status_code
    add_user_to_group_mock.assert_called_once()


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.remove_user_from_group')
def test_remove_from_group(
    remove_user_from_group_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
):

    remove_user_from_group_mock.return_value = {}
    valid_data = {'group_name': 'dummy_group'}

    response = client.post(
        f'/users/{user_id}/groups/remove',
        headers=valid_header,
        json=valid_data,
    )
    assert HTTPStatus.OK == response.status_code
    remove_user_from_group_mock.assert_called_once()
