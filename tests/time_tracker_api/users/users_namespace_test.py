from unittest.mock import Mock, patch
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from utils.azure_users import AzureConnection, ROLE_FIELD_VALUES, AzureUser_v2
from pytest import mark


@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_azure_app_configuration_client'
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.is_toggle_enabled_for_user'
)
@patch('utils.azure_users.AzureConnection.users')
@patch('utils.azure_users.AzureConnection.users_v2')
def test_feature_toggle_is_on_then_role_field_is_list(
    users_v2_mock,
    users_mock,
    is_toggle_enabled_for_user_mock,
    get_azure_app_configuration_client_mock,
    client: FlaskClient,
    valid_header: dict,
):

    is_toggle_enabled_for_user_mock.return_value = True
    users_v2_mock.return_value = [
        {'name': 'dummy', 'email': 'dummy', 'roles': ['dummy-role']}
    ]
    response = client.get('/users', headers=valid_header)

    users_v2_mock.assert_called()
    users_mock.assert_not_called()
    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)[0]
    assert 'email' in json.loads(response.data)[0]
    assert 'roles' in json.loads(response.data)[0]
    assert ['dummy-role'] == json.loads(response.data)[0]['roles']


@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_azure_app_configuration_client'
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.is_toggle_enabled_for_user'
)
@patch('utils.azure_users.AzureConnection.users')
@patch('utils.azure_users.AzureConnection.users_v2')
def test_feature_toggle_is_off_then_role_field_is_string(
    users_v2_mock,
    users_mock,
    is_toggle_enabled_for_user_mock,
    get_azure_app_configuration_client_mock,
    client: FlaskClient,
    valid_header: dict,
):
    is_toggle_enabled_for_user_mock.return_value = False
    users_mock.return_value = [
        {'name': 'dummy', 'email': 'dummy', 'role': 'dummy-role'}
    ]

    response = client.get('/users', headers=valid_header)

    users_mock.assert_called()
    users_v2_mock.assert_not_called()
    assert HTTPStatus.OK == response.status_code
    assert 'name' in json.loads(response.data)[0]
    assert 'email' in json.loads(response.data)[0]
    assert 'role' in json.loads(response.data)[0]
    assert 'dummy-role' == json.loads(response.data)[0]['role']


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


@patch('utils.azure_users.AzureConnection.update_user_role', new_callable=Mock)
def test_on_post_update_user_role_is_being_called_with_valid_arguments(
    update_user_role_mock,
    client: FlaskClient,
    valid_header: dict,
    user_id: str,
):
    update_user_role_mock.return_value = {}
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
    update_user_role_mock.return_value = {}
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
    update_role_mock.return_value = {}
    response = client.post(
        f'/users/{user_id}/roles/{role_id}/{action}', headers=valid_header,
    )

    assert HTTPStatus.OK == response.status_code
    update_role_mock.assert_called_once_with(
        user_id, role_id, is_grant=is_grant
    )


@patch('msal.ConfidentialClientApplication')
@patch('utils.azure_users.AzureConnection.get_token')
@patch('utils.azure_users.AzureConnection._get_user')
@mark.parametrize(
    'field_name,field_value,expected',
    [
        (ROLE_FIELD_VALUES['test'][0], ROLE_FIELD_VALUES['test'][1], True),
        (ROLE_FIELD_VALUES['test'][0], None, False),
    ],
)
def test_azure_connection_is_test_user(
    _get_user_mock,
    get_token_mock,
    msal_client_mock,
    field_name,
    field_value,
    expected,
):
    _get_user_mock.return_value = {field_name: field_value}
    test_user_id = 'test-user-id'

    az_conn = AzureConnection()
    assert az_conn.is_test_user(test_user_id) == expected


@patch('msal.ConfidentialClientApplication')
@patch('utils.azure_users.AzureConnection.get_token')
@patch('utils.azure_users.AzureConnection._get_test_user_ids')
def test_azure_connection_get_test_user_ids(
    _get_test_user_ids_mock, get_token_mock, msal_client_mock,
):
    _get_test_user_ids_mock.return_value = [
        {'objectId': 'ID1'},
        {'objectId': 'ID2'},
    ]
    ids = ['ID1', 'ID2']
    az_conn = AzureConnection()
    assert az_conn.get_test_user_ids() == ids


@patch('msal.ConfidentialClientApplication')
@patch('utils.azure_users.AzureConnection.get_token')
@patch('utils.azure_users.AzureConnection.get_test_user_ids')
@patch('utils.azure_users.AzureConnection.users_v2')
def test_azure_connection_get_non_test_users(
    users_v2_mock, get_test_user_ids_mock, get_token_mock, msal_client_mock,
):
    az1 = AzureUser_v2('ID1', None, None, [])
    az2 = AzureUser_v2('ID2', None, None, [])
    users_v2_mock.return_value = [az1, az2]
    get_test_user_ids_mock.return_value = ['ID1']
    non_test_users = [az2]
    az_conn = AzureConnection()
    assert az_conn.get_non_test_users() == non_test_users
