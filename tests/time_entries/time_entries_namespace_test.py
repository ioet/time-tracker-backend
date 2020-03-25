from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

fake = Faker()

valid_time_entry_input = {
    "project_id": fake.random_int(1, 9999),
    "activity_id": fake.random_int(1, 9999),
    "technologies": fake.words(3, ['java', 'javascript', 'python', 'azure'], unique=True),
    "description": fake.paragraph(nb_sentences=2),
    "start_date": fake.iso8601(end_datetime=None),
    "end_date": fake.iso8601(end_datetime=None),
}
fake_time_entry = ({
    "id": fake.random_int(1, 9999),
    "running": True,
}).update(valid_time_entry_input)


def test_create_time_entry_should_succeed_with_valid_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_create_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'create',
                                                 return_value=fake_time_entry)

    response = client.post("/time-entries", json=valid_time_entry_input, follow_redirects=True)

    assert HTTPStatus.CREATED == response.status_code
    repository_create_mock.assert_called_once_with(valid_time_entry_input)


def test_create_time_entry_should_reject_bad_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    invalid_time_entry_input = valid_time_entry_input.copy().update({
        "project_id": None,
    })
    repository_create_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'create',
                                                 return_value=fake_time_entry)

    response = client.post("/time-entries", json=invalid_time_entry_input, follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_create_mock.assert_not_called()


def test_list_all_time_entries(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_find_all_mock = mocker.patch.object(time_entries_dao.repository,
                                                   'find_all',
                                                   return_value=[])

    response = client.get("/time-entries", follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    repository_find_all_mock.assert_called_once()


def test_get_time_entry_should_succeed_with_valid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    valid_id = fake.random_int(1, 9999)
    repository_find_mock = mocker.patch.object(time_entries_dao.repository,
                                               'find',
                                               return_value=fake_time_entry)

    response = client.get("/time-entries/%s" % valid_id, follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_time_entry == json.loads(response.data)
    repository_find_mock.assert_called_once_with(str(valid_id))


def test_get_time_entry_should_response_with_unprocessable_entity_for_invalid_id_format(client: FlaskClient,
                                                                                        mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.word()

    repository_find_mock = mocker.patch.object(time_entries_dao.repository,
                                               'find',
                                               side_effect=UnprocessableEntity)

    response = client.get("/time-entries/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id))


def test_update_time_entry_should_succeed_with_valid_data(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'update',
                                                 return_value=fake_time_entry)

    valid_id = fake.random_int(1, 9999)
    response = client.put("/time-entries/%s" % valid_id,
                          json=valid_time_entry_input,
                          follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_time_entry == json.loads(response.data)
    repository_update_mock.assert_called_once_with(str(valid_id), valid_time_entry_input)


def test_update_time_entry_should_reject_bad_request(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    invalid_time_entry_data = valid_time_entry_input.copy().update({
        "project_id": 'anything',
    })
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'update',
                                                 return_value=fake_time_entry)
    valid_id = fake.random_int(1, 9999)

    response = client.put("/time-entries/%s" % valid_id,
                          json=invalid_time_entry_data,
                          follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_update_mock.assert_not_called()


def test_update_time_entry_should_return_not_found_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import NotFound
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'update',
                                                 side_effect=NotFound)
    invalid_id = fake.random_int(1, 9999)

    response = client.put("/time-entries/%s" % invalid_id,
                          json=valid_time_entry_input,
                          follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(str(invalid_id), valid_time_entry_input)


def test_delete_time_entry_should_succeed_with_valid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_remove_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'remove',
                                                 return_value=None)
    valid_id = fake.random_int(1, 9999)

    response = client.delete("/time-entries/%s" % valid_id, follow_redirects=True)

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    repository_remove_mock.assert_called_once_with(str(valid_id))


def test_delete_time_entry_should_return_not_found_with_invalid_id(client: FlaskClient,
                                                                   mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import NotFound
    repository_remove_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'remove',
                                                 side_effect=NotFound)
    invalid_id = fake.random_int(1, 9999)

    response = client.delete("/time-entries/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id))


def test_delete_time_entry_should_return_unprocessable_entity_for_invalid_id_format(client: FlaskClient,
                                                                                    mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import UnprocessableEntity
    repository_remove_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'remove',
                                                 side_effect=UnprocessableEntity)
    invalid_id = fake.word()

    response = client.delete("/time-entries/%s" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id))


def test_stop_time_entry_with_valid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'update',
                                                 return_value=fake_time_entry)
    valid_id = fake.random_int(1, 9999)

    response = client.post("/time-entries/%s/stop" % valid_id, follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    repository_update_mock.assert_called_once_with(str(valid_id), {
        "end_date": mocker.ANY
    })


def test_stop_time_entry_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import UnprocessableEntity
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'update',
                                                 side_effect=UnprocessableEntity)
    invalid_id = fake.word()

    response = client.post("/time-entries/%s/stop" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_update_mock.assert_called_once_with(invalid_id, {
        "end_date": mocker.ANY
    })


def test_restart_time_entry_with_valid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'update',
                                                 return_value=fake_time_entry)
    valid_id = fake.random_int(1, 9999)

    response = client.post("/time-entries/%s/restart" % valid_id, follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    repository_update_mock.assert_called_once_with(str(valid_id), {
        "end_date": None
    })


def test_restart_time_entry_with_invalid_id(client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import UnprocessableEntity
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'update',
                                                 side_effect=UnprocessableEntity)
    invalid_id = fake.word()

    response = client.post("/time-entries/%s/restart" % invalid_id, follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_update_mock.assert_called_once_with(invalid_id, {
        "end_date": None
    })
