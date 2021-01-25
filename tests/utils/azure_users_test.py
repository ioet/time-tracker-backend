from unittest.mock import Mock, patch
from utils.azure_users import AzureConnection, ROLE_FIELD_VALUES
from pytest import mark


@patch('msal.ConfidentialClientApplication', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('requests.get')
@mark.parametrize(
    'field_name,field_value,is_test_user_expected_value',
    [
        (ROLE_FIELD_VALUES['test'][0], ROLE_FIELD_VALUES['test'][1], True),
        (ROLE_FIELD_VALUES['test'][0], None, False),
    ],
)
def test_azure_connection_is_test_user(
    get_mock, field_name, field_value, is_test_user_expected_value,
):
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json = Mock(return_value={field_name: field_value})
    get_mock.return_value = response_mock

    test_user_id = 'test-user-id'
    az_conn = AzureConnection()
    assert az_conn.is_test_user(test_user_id) == is_test_user_expected_value


@patch('msal.ConfidentialClientApplication', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('requests.get')
def test_azure_connection_get_test_user_ids(get_mock,):

    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json = Mock(
        return_value={'value': [{'objectId': 'ID1'}, {'objectId': 'ID2'},]}
    )
    get_mock.return_value = response_mock

    ids = ['ID1', 'ID2']
    az_conn = AzureConnection()
    assert az_conn.get_test_user_ids() == ids
