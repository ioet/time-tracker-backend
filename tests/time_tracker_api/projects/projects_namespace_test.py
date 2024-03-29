from unittest.mock import ANY

from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

from time_tracker_api.projects.projects_model import ProjectCosmosDBDao
from utils.enums.status import Status

fake = Faker()

valid_project_data = {
    "name": fake.company(),
    "description": fake.paragraph(),
    'customer_id': fake.uuid4(),
    'project_type_id': fake.uuid4(),
    'technologies': ["python", "faker", "openapi"],
}

fake_project = ({"id": fake.random_int(1, 9999)}).update(valid_project_data)


def test_create_project_should_succeed_with_valid_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao

    repository_create_mock = mocker.patch.object(
        project_dao.repository, 'create', return_value=fake_project
    )
    response = client.post(
        "/projects",
        headers=valid_header,
        json=valid_project_data,
        follow_redirects=True,
    )

    assert HTTPStatus.CREATED == response.status_code
    repository_create_mock.assert_called_once()


def test_create_project_should_reject_bad_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao

    invalid_project_data = valid_project_data.copy()
    invalid_project_data.update(
        {
            "project_type_id": fake.pyint(min_value=1, max_value=100),
        }
    )
    repository_create_mock = mocker.patch.object(
        project_dao.repository, 'create', return_value=fake_project
    )

    response = client.post(
        "/projects",
        headers=valid_header,
        json=invalid_project_data,
        follow_redirects=True,
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_create_mock.assert_not_called()


def test_list_all_projects(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao

    repository_find_all_mock = mocker.patch.object(
        project_dao.repository, 'find_all', return_value=[]
    )

    response = client.get(
        "/projects", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    repository_find_all_mock.assert_called_once()


def test_list_all_active_projects(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao

    repository_find_all_mock = mocker.patch.object(
        project_dao.repository, 'find_all', return_value=[]
    )

    response = client.get(
        "/projects?status=active", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    repository_find_all_mock.assert_called_once()


def test_get_project_should_succeed_with_valid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    valid_id = fake.random_int(1, 9999)

    project_dao_get = mocker.patch.object(ProjectCosmosDBDao, 'get')
    project_dao_get.return_value = fake_project

    response = client.get(
        "/projects/%s" % valid_id, headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    project_dao_get.assert_called_with(str(valid_id))


def test_get_project_should_return_not_found_with_invalid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_find_mock = mocker.patch.object(
        project_dao.repository, 'find', side_effect=NotFound
    )

    response = client.get(
        "/projects/%s" % invalid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id), ANY)


def test_get_project_should_response_with_unprocessable_entity_for_invalid_id_format(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_find_mock = mocker.patch.object(
        project_dao.repository, 'find', side_effect=UnprocessableEntity
    )

    response = client.get(
        "/projects/%s" % invalid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id), ANY)


def test_update_project_should_succeed_with_valid_data(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao

    repository_update_mock = mocker.patch.object(
        project_dao.repository, 'partial_update', return_value=fake_project
    )

    valid_id = fake.random_int(1, 9999)
    response = client.put(
        "/projects/%s" % valid_id,
        headers=valid_header,
        json=valid_project_data,
        follow_redirects=True,
    )

    assert HTTPStatus.OK == response.status_code
    fake_project == json.loads(response.data)
    repository_update_mock.assert_called_once_with(
        str(valid_id), valid_project_data, ANY
    )


def test_update_project_should_reject_bad_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao

    invalid_project_data = valid_project_data.copy()
    invalid_project_data.update(
        {
            "project_type_id": fake.pyint(min_value=1, max_value=100),
        }
    )
    repository_update_mock = mocker.patch.object(
        project_dao.repository, 'partial_update', return_value=fake_project
    )

    valid_id = fake.random_int(1, 9999)
    response = client.put(
        "/projects/%s" % valid_id,
        headers=valid_header,
        json=invalid_project_data,
        follow_redirects=True,
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_update_mock.assert_not_called()


def test_update_project_should_return_not_found_with_invalid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_update_mock = mocker.patch.object(
        project_dao.repository, 'partial_update', side_effect=NotFound
    )

    response = client.put(
        "/projects/%s" % invalid_id,
        headers=valid_header,
        json=valid_project_data,
        follow_redirects=True,
    )

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(
        str(invalid_id), valid_project_data, ANY
    )


def test_delete_project_should_succeed_with_valid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao

    valid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(
        project_dao.repository, 'partial_update', return_value=None
    )

    response = client.delete(
        "/projects/%s" % valid_id, headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    repository_remove_mock.assert_called_once_with(
        str(valid_id), {'status': Status.INACTIVE.value}, ANY
    )


def test_delete_project_should_return_not_found_with_invalid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(
        project_dao.repository, 'partial_update', side_effect=NotFound
    )

    response = client.delete(
        "/projects/%s" % invalid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_remove_mock.assert_called_once_with(
        str(invalid_id), {'status': Status.INACTIVE.value}, ANY
    )


def test_delete_project_should_return_unprocessable_entity_for_invalid_id_format(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.projects.projects_namespace import project_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_remove_mock = mocker.patch.object(
        project_dao.repository,
        'partial_update',
        side_effect=UnprocessableEntity,
    )

    response = client.delete(
        "/projects/%s" % invalid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_remove_mock.assert_called_once_with(
        str(invalid_id), {'status': Status.INACTIVE.value}, ANY
    )


def test_get_recent_projects_should_call_method_get_recent_projects_from_project_dao(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    project_dao_get_recent_projects_mock = mocker.patch.object(
        ProjectCosmosDBDao, 'get_recent_projects', return_value=[]
    )

    response = client.get(
        "/projects/recent",
        headers=valid_header,
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    project_dao_get_recent_projects_mock.assert_called_once()
