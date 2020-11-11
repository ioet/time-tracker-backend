from unittest.mock import ANY, Mock, patch

# from mock import patch

from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture


@patch(
    'utils.azure_users.AzureConnection.users',
    new_callable=Mock(return_value=[{'name': 'dummy', 'email': 'dummy'}]),
)
@patch('utils.azure_users.AzureConnection', new_callable=Mock)
@patch('msal.ConfidentialClientApplication', new_callable=Mock)
@patch(
    'msal.ConfidentialClientApplication.acquire_token_for_client',
    new_callable=Mock,
)
def test_users_response_contains_expected_props(
    acquire_token_method,
    msal_client,
    azure_connection,
    users_method,
    client: FlaskClient,
    valid_header: dict,
):

    # from time_tracker_api.users.users_namespace import azure_connection
    # azure_connection.users = Mock(return_value=[{'name':'dummy', 'email': 'dummy'}])

    response = client.get('/time-entries/users', headers=valid_header,)

    assert 'name' in json.loads(response.data)[0]
    assert 'email' in json.loads(response.data)[0]
