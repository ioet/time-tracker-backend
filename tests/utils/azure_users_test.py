from unittest.mock import Mock, patch
from utils.azure_users import AzureConnection, ROLE_FIELD_VALUES, AzureUser
from pytest import mark


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
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


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('requests.get')
def test_azure_connection_get_test_user_ids(get_mock):
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json = Mock(
        return_value={'value': [{'objectId': 'ID1'}, {'objectId': 'ID2'},]}
    )
    get_mock.return_value = response_mock

    ids = ['ID1', 'ID2']
    az_conn = AzureConnection()
    assert az_conn.get_test_user_ids() == ids


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.get_test_user_ids')
@patch('utils.azure_users.AzureConnection.users')
def test_azure_connection_get_non_test_users(
    users_mock, get_test_user_ids_mock
):
    test_user = AzureUser('ID1', None, None, [], [])
    non_test_user = AzureUser('ID2', None, None, [], [])
    users_mock.return_value = [test_user, non_test_user]
    get_test_user_ids_mock.return_value = ['ID1']
    non_test_users = [non_test_user]
    az_conn = AzureConnection()
    assert az_conn.get_non_test_users() == non_test_users


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('requests.get')
def test_azure_connection_get_group_id_by_group_name(get_mock):
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json = Mock(return_value={'value': [{'objectId': 'ID1'}]})
    get_mock.return_value = response_mock

    group_id = 'ID1'
    azure_connection = AzureConnection()
    assert (
        azure_connection.get_group_id_by_group_name('group_name') == group_id
    )


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.get_group_id_by_group_name')
@patch('requests.post')
@mark.parametrize('expected_value', [True, False])
def test_is_user_in_group(
    post_mock, get_group_id_by_group_name_mock, expected_value
):
    response_expected = {'value': expected_value}
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json = Mock(return_value=response_expected)
    post_mock.return_value = response_mock

    get_group_id_by_group_name_mock.return_value = 'group_id'
    payload_mock = {'group_name': 'group_id'}

    azure_connection = AzureConnection()
    assert (
        azure_connection.is_user_in_group('user_id', payload_mock)
        == response_expected
    )


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('requests.get')
def test_get_groups_and_users(get_mock):
    response_mock = Mock()
    response_mock.status_code = 200
    return_value = {
        'value': [
            {
                'displayName': 'test-group-1',
                'members': [
                    {'objectId': 'user-id1'},
                    {'objectId': 'user-id2'},
                ],
            },
            {
                'displayName': 'test-group-2',
                'members': [
                    {'objectId': 'user-id3'},
                    {'objectId': 'user-id1'},
                ],
            },
            {'displayName': 'test-group-3', 'members': [],},
        ]
    }
    response_mock.json = Mock(return_value=return_value)
    get_mock.return_value = response_mock

    expected_result = [
        ('test-group-1', ['user-id1', 'user-id2']),
        ('test-group-2', ['user-id3', 'user-id1']),
        ('test-group-3', []),
    ]

    azure_connection = AzureConnection()

    assert azure_connection.get_groups_and_users() == expected_result


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.get_groups_and_users')
@mark.parametrize(
    'user_id,groups_expected_value',
    [
        ('user-id1', ['test-group-1', 'test-group-2']),
        ('user-id2', ['test-group-1']),
        ('user-id3', ['test-group-2']),
        ('user-id4', []),
    ],
)
def test_get_groups_by_user_id(
    get_groups_and_users_mock, user_id, groups_expected_value
):
    get_groups_and_users_mock.return_value = [
        ('test-group-1', ['user-id1', 'user-id2']),
        ('test-group-2', ['user-id3', 'user-id1']),
    ]

    azure_connection = AzureConnection()
    groups = azure_connection.get_groups_by_user_id(user_id)
    assert groups == groups_expected_value


@patch('utils.azure_users.AzureConnection.get_msal_client', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.get_groups_and_users')
def test_get_groups_and_users_called_once_by_instance(
    get_groups_and_users_mock,
):
    get_groups_and_users_mock.return_value = []
    user_id = 'user-id1'
    azure_connection = AzureConnection()
    azure_connection.get_groups_by_user_id(user_id)
    azure_connection.get_groups_by_user_id(user_id)
    azure_connection.get_groups_by_user_id(user_id)

    get_groups_and_users_mock.assert_called_once()
