from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

fake = Faker()

valid_activity_data = {
    "name": fake.company(),
    "description": fake.paragraph(),
    "tenant_id": fake.uuid4()
}

fake_activity = ({
    "id": fake.random_int(1, 9999)
}).update(valid_activity_data)


def test_create_activity_should_succeed_with_valid_request(client: FlaskClient,
                                                           mocker: MockFixture,
                                                           valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao
    repository_create_mock = mocker.patch.object(activity_dao.repository,
                                                 'create',
                                                 return_value=fake_activity)

    response = client.post("/activities",
                           headers=valid_header,
                           json=valid_activity_data,
                           follow_redirects=True)

    assert HTTPStatus.CREATED == response.status_code
    repository_create_mock.assert_called_once()


def test_create_activity_should_reject_bad_request(client: FlaskClient,
                                                   mocker: MockFixture,
                                                   valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao
    repository_create_mock = mocker.patch.object(activity_dao.repository,
                                                 'create',
                                                 return_value=fake_activity)

    response = client.post("/activities",
                           headers=valid_header,
                           json=None,
                           follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_create_mock.assert_not_called()


def test_list_all_activities(client: FlaskClient,
                             mocker: MockFixture,
                             tenant_id: str,
                             valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao
    repository_find_all_mock = mocker.patch.object(activity_dao.repository,
                                                   'find_all',
                                                   return_value=[])

    response = client.get("/activities",
                          headers=valid_header,
                          follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    json_data = json.loads(response.data)
    assert [] == json_data
    repository_find_all_mock.assert_called_once_with(partition_key_value=tenant_id,
                                                     conditions={})


def test_get_activity_should_succeed_with_valid_id(client: FlaskClient,
                                                   mocker: MockFixture,
                                                   tenant_id: str,
                                                   valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao

    valid_id = fake.random_int(1, 9999)

    repository_find_mock = mocker.patch.object(activity_dao.repository,
                                               'find',
                                               return_value=fake_activity)

    response = client.get("/activities/%s" % valid_id,
                          headers=valid_header,
                          follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_activity == json.loads(response.data)
    repository_find_mock.assert_called_once_with(str(valid_id), partition_key_value=tenant_id)


def test_get_activity_should_return_not_found_with_invalid_id(client: FlaskClient,
                                                              mocker: MockFixture,
                                                              tenant_id: str,
                                                              valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_find_mock = mocker.patch.object(activity_dao.repository,
                                               'find',
                                               side_effect=NotFound)

    response = client.get("/activities/%s" % invalid_id,
                          headers=valid_header,
                          follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id),
                                                 partition_key_value=tenant_id)


def test_get_activity_should_return_422_for_invalid_id_format(client: FlaskClient,
                                                              mocker: MockFixture):
    from time_tracker_api.activities.activities_namespace import activity_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_find_mock = mocker.patch.object(activity_dao.repository,
                                               'find',
                                               side_effect=UnprocessableEntity)

    response = client.get("/activities/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_find_mock.assert_not_called()


def test_update_activity_should_succeed_with_valid_data(client: FlaskClient,
                                                        tenant_id: str,
                                                        mocker: MockFixture,
                                                        valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao

    repository_update_mock = mocker.patch.object(activity_dao.repository,
                                                 'partial_update',
                                                 return_value=fake_activity)

    valid_id = fake.uuid4()
    response = client.put("/activities/%s" % valid_id,
                          headers=valid_header,
                          json=valid_activity_data,
                          follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_activity == json.loads(response.data)
    repository_update_mock.assert_called_once_with(str(valid_id),
                                                   changes=valid_activity_data,
                                                   partition_key_value=tenant_id)


def test_update_activity_should_reject_bad_request(client: FlaskClient,
                                                   mocker: MockFixture,
                                                   valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao
    repository_update_mock = mocker.patch.object(activity_dao.repository,
                                                 'partial_update',
                                                 return_value=fake_activity)

    valid_id = fake.random_int(1, 9999)
    response = client.put("/activities/%s" % valid_id,
                          headers=valid_header,
                          json=None,
                          follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_update_mock.assert_not_called()


def test_update_activity_should_return_not_found_with_invalid_id(client: FlaskClient,
                                                                 tenant_id: str,
                                                                 mocker: MockFixture,
                                                                 valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_update_mock = mocker.patch.object(activity_dao.repository,
                                                 'partial_update',
                                                 side_effect=NotFound)

    response = client.put("/activities/%s" % invalid_id,
                          headers=valid_header,
                          json=valid_activity_data,
                          follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(str(invalid_id),
                                                   changes=valid_activity_data,
                                                   partition_key_value=tenant_id)


def test_delete_activity_should_succeed_with_valid_id(client: FlaskClient,
                                                      mocker: MockFixture,
                                                      tenant_id: str,
                                                      valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao

    valid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(activity_dao.repository,
                                                 'delete',
                                                 return_value=None)

    response = client.delete("/activities/%s" % valid_id,
                             headers=valid_header,
                             follow_redirects=True)

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    repository_remove_mock.assert_called_once_with(str(valid_id),
                                                   partition_key_value=tenant_id)


def test_delete_activity_should_return_not_found_with_invalid_id(client: FlaskClient,
                                                                 mocker: MockFixture,
                                                                 tenant_id: str,
                                                                 valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao
    from werkzeug.exceptions import NotFound

    invalid_id = fake.random_int(1, 9999)

    repository_remove_mock = mocker.patch.object(activity_dao.repository,
                                                 'delete',
                                                 side_effect=NotFound)

    response = client.delete("/activities/%s" % invalid_id,
                             headers=valid_header,
                             follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id),
                                                   partition_key_value=tenant_id)


def test_delete_activity_should_return_422_for_invalid_id_format(client: FlaskClient,
                                                                 mocker: MockFixture,
                                                                 tenant_id: str,
                                                                 valid_header: dict):
    from time_tracker_api.activities.activities_namespace import activity_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.company()

    repository_remove_mock = mocker.patch.object(activity_dao.repository,
                                                 'delete',
                                                 side_effect=UnprocessableEntity)

    response = client.delete("/activities/%s" % invalid_id,
                             headers=valid_header,
                             follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id),
                                                   partition_key_value=tenant_id)
