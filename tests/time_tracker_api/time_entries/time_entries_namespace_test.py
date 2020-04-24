from datetime import timedelta
from unittest.mock import ANY

from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

from commons.data_access_layer.cosmos_db import current_datetime, current_datetime_str

fake = Faker()

yesterday = current_datetime() - timedelta(days=1)
valid_time_entry_input = {
    "project_id": fake.uuid4(),
    "activity_id": fake.uuid4(),
    "description": fake.paragraph(nb_sentences=2),
    "start_date": current_datetime_str(),
}

fake_time_entry = ({
    "id": fake.random_int(1, 9999),
    "running": True,
    "owner_id": fake.uuid4(),
    "tenant_id": fake.uuid4(),
})
fake_time_entry.update(valid_time_entry_input)


def test_create_time_entry_with_invalid_date_range_should_raise_bad_request_error(client: FlaskClient,
                                                                                  mocker: MockFixture,
                                                                                  valid_header: dict):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_container_create_item_mock = mocker.patch.object(time_entries_dao.repository.container,
                                                                'create_item',
                                                                return_value=fake_time_entry)

    invalid_time_entry_input = valid_time_entry_input.copy()
    invalid_time_entry_input.update({
        "end_date": str(yesterday.isoformat())
    })
    response = client.post("/time-entries",
                           headers=valid_header,
                           json=invalid_time_entry_input,
                           follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_container_create_item_mock.assert_not_called()


def test_create_time_entry_with_end_date_in_future_should_raise_bad_request_error(client: FlaskClient,
                                                                                  mocker: MockFixture,
                                                                                  valid_header: dict):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_container_create_item_mock = mocker.patch.object(time_entries_dao.repository.container,
                                                                'create_item',
                                                                return_value=fake_time_entry)
    invalid_time_entry_input = valid_time_entry_input.copy()
    invalid_time_entry_input.update({
        "end_date": str(fake.future_datetime().isoformat())
    })
    response = client.post("/time-entries",
                           headers=valid_header,
                           json=invalid_time_entry_input,
                           follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_container_create_item_mock.assert_not_called()


def test_create_time_entry_should_succeed_with_valid_request(client: FlaskClient,
                                                             mocker: MockFixture,
                                                             valid_header: dict):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_create_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'create',
                                                 return_value=fake_time_entry)

    response = client.post("/time-entries",
                           headers=valid_header,
                           json=valid_time_entry_input,
                           follow_redirects=True)

    assert HTTPStatus.CREATED == response.status_code
    repository_create_mock.assert_called_once()


def test_create_time_entry_with_missing_req_field_should_return_bad_request(client: FlaskClient,
                                                                            mocker: MockFixture,
                                                                            valid_header: dict):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_create_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'create',
                                                 return_value=fake_time_entry)

    response = client.post("/time-entries",
                           headers=valid_header,
                           json={
                               "activity_id": fake.uuid4(),
                               "start_date": current_datetime_str(),
                           },
                           follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_create_mock.assert_not_called()


def test_list_all_time_entries(client: FlaskClient,
                               mocker: MockFixture,
                               valid_header: dict):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_find_all_mock = mocker.patch.object(time_entries_dao.repository,
                                                   'find_all',
                                                   return_value=[])

    response = client.get("/time-entries",
                          headers=valid_header,
                          follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    repository_find_all_mock.assert_called_once()


def test_get_time_entry_should_succeed_with_valid_id(client: FlaskClient,
                                                     mocker: MockFixture,
                                                     valid_header: dict,
                                                     tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_find_mock = mocker.patch.object(time_entries_dao.repository,
                                               'find',
                                               return_value=fake_time_entry)

    valid_id = fake.random_int(1, 9999)
    response = client.get("/time-entries/%s" % valid_id,
                          headers=valid_header,
                          follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_time_entry == json.loads(response.data)
    repository_find_mock.assert_called_once_with(str(valid_id),
                                                 partition_key_value=tenant_id,
                                                 peeker=ANY)


def test_get_time_entry_should_response_with_unprocessable_entity_for_invalid_id_format(client: FlaskClient,
                                                                                        mocker: MockFixture,
                                                                                        valid_header: dict,
                                                                                        tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import UnprocessableEntity

    invalid_id = fake.word()

    repository_find_mock = mocker.patch.object(time_entries_dao.repository,
                                               'find',
                                               side_effect=UnprocessableEntity)

    response = client.get("/time-entries/%s" % invalid_id,
                          headers=valid_header,
                          follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_find_mock.assert_called_once_with(str(invalid_id),
                                                 partition_key_value=tenant_id,
                                                 peeker=ANY)


def test_update_time_entry_should_succeed_with_valid_data(client: FlaskClient,
                                                          mocker: MockFixture,
                                                          valid_header: dict,
                                                          tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'partial_update',
                                                 return_value=fake_time_entry)

    valid_id = fake.random_int(1, 9999)
    response = client.put("/time-entries/%s" % valid_id,
                          headers=valid_header,
                          json=valid_time_entry_input,
                          follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    fake_time_entry == json.loads(response.data)
    repository_update_mock.assert_called_once_with(str(valid_id),
                                                   changes=valid_time_entry_input,
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_update_time_entry_should_reject_bad_request(client: FlaskClient,
                                                     mocker: MockFixture,
                                                     valid_header: dict,
                                                     tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    invalid_time_entry_data = valid_time_entry_input.copy()
    invalid_time_entry_data.update({
        "project_id": fake.pyint(min_value=1, max_value=100),
    })
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'update',
                                                 return_value=fake_time_entry)
    valid_id = fake.random_int(1, 9999)

    response = client.put("/time-entries/%s" % valid_id,
                          headers=valid_header,
                          json=invalid_time_entry_data,
                          follow_redirects=True)

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_update_mock.assert_not_called()


def test_update_time_entry_should_return_not_found_with_invalid_id(client: FlaskClient,
                                                                   mocker: MockFixture,
                                                                   valid_header: dict,
                                                                   tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import NotFound
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'partial_update',
                                                 side_effect=NotFound)
    invalid_id = fake.random_int(1, 9999)

    response = client.put("/time-entries/%s" % invalid_id,
                          headers=valid_header,
                          json=valid_time_entry_input,
                          follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(str(invalid_id),
                                                   changes=valid_time_entry_input,
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_delete_time_entry_should_succeed_with_valid_id(client: FlaskClient,
                                                        mocker: MockFixture,
                                                        valid_header: dict,
                                                        tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_remove_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'delete',
                                                 return_value=None)
    valid_id = fake.random_int(1, 9999)

    response = client.delete("/time-entries/%s" % valid_id,
                             headers=valid_header,
                             follow_redirects=True)

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    repository_remove_mock.assert_called_once_with(str(valid_id),
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_delete_time_entry_should_return_not_found_with_invalid_id(client: FlaskClient,
                                                                   mocker: MockFixture,
                                                                   valid_header: dict,
                                                                   tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import NotFound
    repository_remove_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'delete',
                                                 side_effect=NotFound)
    invalid_id = fake.random_int(1, 9999)

    response = client.delete("/time-entries/%s" % invalid_id,
                             headers=valid_header,
                             follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id),
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_delete_time_entry_should_return_unprocessable_entity_for_invalid_id_format(client: FlaskClient,
                                                                                    mocker: MockFixture,
                                                                                    valid_header: dict,
                                                                                    tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import UnprocessableEntity
    repository_remove_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'delete',
                                                 side_effect=UnprocessableEntity)
    invalid_id = fake.word()

    response = client.delete("/time-entries/%s" % invalid_id,
                             headers=valid_header,
                             follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_remove_mock.assert_called_once_with(str(invalid_id),
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_stop_time_entry_with_valid_id(client: FlaskClient,
                                       mocker: MockFixture,
                                       valid_header: dict,
                                       tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'partial_update',
                                                 return_value=fake_time_entry)
    valid_id = fake.random_int(1, 9999)

    response = client.post("/time-entries/%s/stop" % valid_id,
                           headers=valid_header,
                           follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    repository_update_mock.assert_called_once_with(str(valid_id),
                                                   changes={"end_date": mocker.ANY},
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_stop_time_entry_with_id_with_invalid_format(client: FlaskClient,
                                                     mocker: MockFixture,
                                                     valid_header: dict,
                                                     tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import UnprocessableEntity
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'partial_update',
                                                 side_effect=UnprocessableEntity)
    invalid_id = fake.word()

    response = client.post("/time-entries/%s/stop" % invalid_id,
                           headers=valid_header,
                           follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_update_mock.assert_called_once_with(invalid_id,
                                                   changes={"end_date": ANY},
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_restart_time_entry_with_valid_id(client: FlaskClient,
                                          mocker: MockFixture,
                                          valid_header: dict,
                                          tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'partial_update',
                                                 return_value=fake_time_entry)
    valid_id = fake.random_int(1, 9999)

    response = client.post("/time-entries/%s/restart" % valid_id,
                           headers=valid_header,
                           follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    repository_update_mock.assert_called_once_with(str(valid_id),
                                                   changes={"end_date": None},
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_restart_time_entry_with_id_with_invalid_format(client: FlaskClient,
                                                        mocker: MockFixture,
                                                        valid_header: dict,
                                                        tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    from werkzeug.exceptions import UnprocessableEntity
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'partial_update',
                                                 side_effect=UnprocessableEntity,
                                                 peeker=ANY)
    invalid_id = fake.word()

    response = client.post("/time-entries/%s/restart" % invalid_id,
                           headers=valid_header,
                           follow_redirects=True)

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    repository_update_mock.assert_called_once_with(invalid_id,
                                                   changes={"end_date": None},
                                                   partition_key_value=tenant_id,
                                                   peeker=ANY)


def test_get_running_should_call_find_running(client: FlaskClient,
                                              mocker: MockFixture,
                                              valid_header: dict,
                                              owner_id: str,
                                              tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'find_running',
                                                 return_value=fake_time_entry)

    response = client.get("/time-entries/running",
                          headers=valid_header,
                          follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    assert json.loads(response.data) is not None
    repository_update_mock.assert_called_once_with(partition_key_value=tenant_id,
                                                   owner_id=owner_id)


def test_get_running_should_return_not_found_if_find_running_throws_StopIteration(client: FlaskClient,
                                                                                  mocker: MockFixture,
                                                                                  valid_header: dict,
                                                                                  owner_id: str,
                                                                                  tenant_id: str):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    repository_update_mock = mocker.patch.object(time_entries_dao.repository,
                                                 'find_running',
                                                 side_effect=StopIteration)

    response = client.get("/time-entries/running",
                          headers=valid_header,
                          follow_redirects=True)

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(partition_key_value=tenant_id,
                                                   owner_id=owner_id)
