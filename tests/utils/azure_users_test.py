from unittest.mock import Mock, patch
from utils.azure_users import AzureConnection, ROLE_FIELD_VALUES, AzureUser_v2
from pytest import mark


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
    _get_test_user_ids_mock,
    get_token_mock,
    msal_client_mock,
):
    _get_test_user_ids_mock.return_value = [
        {'objectId': 'ID1'},
        {'objectId': 'ID2'},
    ]
    ids = ['ID1', 'ID2']
    az_conn = AzureConnection()
    assert az_conn.get_test_user_ids() == ids
