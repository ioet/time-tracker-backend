from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

from time_tracker_api.projects.projects_model import PROJECT_TYPE

fake = Faker()

valid_project_data = {
    "name": fake.company(),
    "description": fake.paragraph(),
    "type": fake.word(PROJECT_TYPE.valid_type_values()),
}
fake_project = ({
    "id": fake.random_int(1, 9999)
}).update(valid_project_data)


def test_create_project_should_succeed_with_valid_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    repository_create_mock = mocker.patch.object(project_dao.repository,
                                                 'create',
                                                 return_value=fake_project)

    response = client.post("/projects", json=valid_project_data, follow_redirects=True)

    assert HTTPStatus.CREATED == response.status_code
    repository_create_mock.assert_called_once_with(valid_project_data)


def test_create_project_should_reject_bad_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    invalid_project_data = valid_project_data.copy().update({
        "type": 'anything',
    })
    repository_create_mock = mocker.patch.object(project_dao.repository,
                                                 'create',
                                                 return_value=fake_project)

    response = client.post("/projects", json=invalid_project_data, follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_create_mock.assert_not_called()


def test_list_all_projects(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    repository_find_all_mock = mocker.patch.object(project_dao.repository,
                                                   'find_all',
                                                   return_value=[])

    response = client.get("/projects", follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    repository_find_all_mock.assert_called_once()


def test_get_project_should_succeed_with_valid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    valid_id = fake.random_int(1, 9999)
    repository_find_mock = mocker.patch.object(project_dao.repository,
                                               'find',
                                               return_value=fake_project)

    response = client.get("/projects/%s" % valid_id, follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_project == json.loads(response.data)
    repository_find_mock.assert_called_once_with(str(valid_id))


def test_get_project_should_return_not_found_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_find_mock = mocker.patch.object(project_dao.repository,
                                               'find',
                                               side_effect=NotFound)

    response = client.get("/projects/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id))


def test_get_project_should_response_with_unprocessable_entity_for_invalid_id_format(client: FlaskClient,
                                                                                     mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_find_mock = mocker.patch.object(project_dao.repository,
                                               'find',
                                               side_effect=UnprocessableEntity)

    response = client.get("/projects/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id))


def test_update_project_should_succeed_with_valid_data(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao

    repository_update_mock = mocker.patch.object(project_dao.repository,
                                                 'update',
                                                 return_value=fake_project)

    valid_id = fake.random_int(1, 9999)
    response = client.put("/projects/%s" % valid_id, json=valid_project_data, follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_project == json.loads(response.data)
    repository_update_mock.assert_called_once_with(str(valid_id), valid_project_data)


def test_update_project_should_reject_bad_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    invalid_project_data = valid_project_data.copy().update({
        "type": 'anything',
    })
    repository_update_mock = mocker.patch.object(project_dao.repository,
                                                 'update',
                                                 return_value=fake_project)

    valid_id = fake.random_int(1, 9999)
    response = client.put("/projects/%s" % valid_id, json=invalid_project_data, follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_update_mock.assert_not_called()


def test_update_project_should_return_not_found_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_update_mock = mocker.patch.object(project_dao.repository,
                                                 'update',
                                                 side_effect=NotFound)

    response = client.put("/projects/%s" % invalid_id,
                          json=valid_project_data,
                          follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(str(invalid_id), valid_project_data)


def test_delete_project_should_succeed_with_valid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao

    valid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(project_dao.repository,
                                                 'remove',
                                                 return_value=None)

    response = client.delete("/projects/%s" % valid_id, follow_redirects=True)

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    repository_remove_mock.assert_called_once_with(str(valid_id))


def test_delete_project_should_return_not_found_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(project_dao.repository,
                                                 'remove',
                                                 side_effect=NotFound)

    response = client.delete("/projects/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id))


def test_delete_project_should_return_unprocessable_entity_for_invalid_id_format(client: FlaskClient,
                                                                                 mocker: MockFixture):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_remove_mock = mocker.patch.object(project_dao.repository,
                                                 'remove',
                                                 side_effect=UnprocessableEntity)

    response = client.delete("/projects/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id))
