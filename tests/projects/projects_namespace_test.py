from flask import json
from flask.testing import FlaskClient
from pytest_mock import MockFixture


def test_list_all_elements(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    repository_find_all_mock = mocker.patch.object(project_dao.repository, 'find_all', return_value=[])

    response = client.get("/projects", follow_redirects=True)

    assert 200 == response.status_code

    json_data = json.loads(response.data)
    assert [] == json_data
    repository_find_all_mock.assert_called_once()
