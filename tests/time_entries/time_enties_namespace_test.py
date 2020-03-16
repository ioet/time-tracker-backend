from flask import json
from flask.testing import FlaskClient
from pytest_mock import MockFixture


def test_list_should_return_empty_array(mocker: MockFixture, client: FlaskClient):
    from time_tracker_api.time_entries.time_entries_namespace import model
    """Should return an empty array"""
    model_mock = mocker.patch.object(model, 'find_all', return_value=[])

    response = client.get("/time-entries", follow_redirects=True)

    assert 200 == response.status_code

    json_data = json.loads(response.data)
    assert [] == json_data
    model_mock.assert_called_once()
