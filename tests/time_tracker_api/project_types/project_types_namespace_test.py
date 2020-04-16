from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

from time_tracker_api.security import current_user_tenant_id

fake = Faker()

valid_project_type_data = {
    "name": fake.company(),
    "description": fake.paragraph(),
    'customer_id': fake.uuid4(),
    'parent_id': fake.uuid4(),
}

fake_project_type = ({
    "id": fake.random_int(1, 9999),
    "tenant_id": fake.uuid4(),
}).update(valid_project_type_data)


def test_create_project_type_should_succeed_with_valid_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    repository_create_mock = mocker.patch.object(project_type_dao.repository,
                                                 'create',
                                                 return_value=fake_project_type)

    response = client.post("/project-types", json=valid_project_type_data, follow_redirects=True)

    assert HTTPStatus.CREATED == response.status_code
    repository_create_mock.assert_called_once()


def test_create_project_type_should_reject_bad_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    invalid_project_type_data = valid_project_type_data.copy()
    invalid_project_type_data.update({
        "parent_id": None,
    })
    repository_create_mock = mocker.patch.object(project_type_dao.repository,
                                                 'create',
                                                 return_value=fake_project_type)

    response = client.post("/project-types", json=invalid_project_type_data, follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_create_mock.assert_not_called()


def test_list_all_project_types(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    repository_find_all_mock = mocker.patch.object(project_type_dao.repository,
                                                   'find_all',
                                                   return_value=[])

    response = client.get("/project-types", follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    repository_find_all_mock.assert_called_once()


def test_get_project_should_succeed_with_valid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    valid_id = fake.random_int(1, 9999)
    repository_find_mock = mocker.patch.object(project_type_dao.repository,
                                               'find',
                                               return_value=fake_project_type)

    response = client.get("/project-types/%s" % valid_id, follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_project_type == json.loads(response.data)
    repository_find_mock.assert_called_once_with(str(valid_id),
                                                 partition_key_value=current_user_tenant_id())


def test_get_project_should_return_not_found_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_find_mock = mocker.patch.object(project_type_dao.repository,
                                               'find',
                                               side_effect=NotFound)

    response = client.get("/project-types/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id),
                                                 partition_key_value=current_user_tenant_id())


def test_get_project_should_response_with_unprocessable_entity_for_invalid_id_format(client: FlaskClient,
                                                                                     mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_find_mock = mocker.patch.object(project_type_dao.repository,
                                               'find',
                                               side_effect=UnprocessableEntity)

    response = client.get("/project-types/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id),
                                                 partition_key_value=current_user_tenant_id())


def test_update_project_should_succeed_with_valid_data(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao

    repository_update_mock = mocker.patch.object(project_type_dao.repository,
                                                 'partial_update',
                                                 return_value=fake_project_type)

    valid_id = fake.random_int(1, 9999)
    response = client.put("/project-types/%s" % valid_id, json=valid_project_type_data, follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_project_type == json.loads(response.data)
    repository_update_mock.assert_called_once_with(str(valid_id),
                                                   changes=valid_project_type_data,
                                                   partition_key_value=current_user_tenant_id())


def test_update_project_should_reject_bad_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    invalid_project_type_data = valid_project_type_data.copy()
    invalid_project_type_data.update({
        "parent_id": None,
    })
    repository_update_mock = mocker.patch.object(project_type_dao.repository,
                                                 'partial_update',
                                                 return_value=fake_project_type)

    valid_id = fake.random_int(1, 9999)
    response = client.put("/project-types/%s" % valid_id, json=invalid_project_type_data, follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_update_mock.assert_not_called()


def test_update_project_should_return_not_found_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_update_mock = mocker.patch.object(project_type_dao.repository,
                                                 'partial_update',
                                                 side_effect=NotFound)

    response = client.put("/project-types/%s" % invalid_id,
                          json=valid_project_type_data,
                          follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(str(invalid_id),
                                                   changes=valid_project_type_data,
                                                   partition_key_value=current_user_tenant_id())


def test_delete_project_should_succeed_with_valid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao

    valid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(project_type_dao.repository,
                                                 'delete',
                                                 return_value=None)

    response = client.delete("/project-types/%s" % valid_id, follow_redirects=True)

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    repository_remove_mock.assert_called_once_with(str(valid_id),
                                                   partition_key_value=current_user_tenant_id())


def test_delete_project_should_return_not_found_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(project_type_dao.repository,
                                                 'delete',
                                                 side_effect=NotFound)

    response = client.delete("/project-types/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id),
                                                   partition_key_value=current_user_tenant_id())


def test_delete_project_should_return_unprocessable_entity_for_invalid_id_format(client: FlaskClient,
                                                                                 mocker: MockFixture):
    from time_tracker_api.project_types.project_types_namespace import project_type_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_remove_mock = mocker.patch.object(project_type_dao.repository,
                                                 'delete',
                                                 side_effect=UnprocessableEntity)

    response = client.delete("/project-types/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id),
                                                   partition_key_value=current_user_tenant_id())
