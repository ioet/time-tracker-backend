from datetime import timedelta
from unittest.mock import ANY, Mock

from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture, pytest

from commons.data_access_layer.cosmos_db import (
    current_datetime,
    current_datetime_str,
    get_current_month,
    get_current_year,
)

from utils import worked_time

from werkzeug.exceptions import NotFound, UnprocessableEntity, HTTPException

fake = Faker()

yesterday = current_datetime() - timedelta(days=1)
valid_time_entry_input = {
    "project_id": fake.uuid4(),
    "activity_id": fake.uuid4(),
    "description": fake.paragraph(nb_sentences=2),
    "start_date": current_datetime_str(),
}

fake_time_entry = {
    "id": fake.random_int(1, 9999),
    "running": True,
    "owner_id": fake.uuid4(),
    "tenant_id": fake.uuid4(),
}
fake_time_entry.update(valid_time_entry_input)


def test_create_time_entry_with_invalid_date_range_should_raise_bad_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    repository_container_create_item_mock = mocker.patch.object(
        time_entries_dao.repository.container,
        'create_item',
        return_value=fake_time_entry,
    )

    invalid_time_entry_input = valid_time_entry_input.copy()
    invalid_time_entry_input.update({"end_date": str(yesterday.isoformat())})
    response = client.post(
        "/time-entries",
        headers=valid_header,
        json=invalid_time_entry_input,
        follow_redirects=True,
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_container_create_item_mock.assert_not_called()


def test_create_time_entry_with_end_date_in_future_should_raise_bad_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    repository_container_create_item_mock = mocker.patch.object(
        time_entries_dao.repository.container,
        'create_item',
        return_value=fake_time_entry,
    )
    invalid_time_entry_input = valid_time_entry_input.copy()
    invalid_time_entry_input.update(
        {"end_date": str(fake.future_datetime().isoformat())}
    )
    response = client.post(
        "/time-entries",
        headers=valid_header,
        json=invalid_time_entry_input,
        follow_redirects=True,
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_container_create_item_mock.assert_not_called()


def test_create_time_entry_should_succeed_with_valid_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    repository_create_mock = mocker.patch.object(
        time_entries_dao.repository, 'create', return_value=fake_time_entry
    )

    response = client.post(
        "/time-entries",
        headers=valid_header,
        json=valid_time_entry_input,
        follow_redirects=True,
    )

    assert HTTPStatus.CREATED == response.status_code
    repository_create_mock.assert_called_once()


def test_create_time_entry_with_missing_req_field_should_return_bad_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    repository_create_mock = mocker.patch.object(
        time_entries_dao.repository, 'create', return_value=fake_time_entry
    )

    response = client.post(
        "/time-entries",
        headers=valid_header,
        json={
            "activity_id": fake.uuid4(),
            "start_date": current_datetime_str(),
        },
        follow_redirects=True,
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_create_mock.assert_not_called()


def test_list_all_time_entries(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    dao_get_all_mock = mocker.patch.object(
        time_entries_dao, 'get_all', return_value=[]
    )

    response = client.get(
        "/time-entries", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    dao_get_all_mock.assert_called_once()


def test_get_time_entry_should_succeed_with_valid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    dao_get_mock = mocker.patch.object(
        time_entries_dao, 'get', return_value={}
    )

    valid_id = fake.random_int(1, 9999)
    response = client.get(
        "/time-entries/%s" % valid_id,
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.OK == response.status_code
    fake_time_entry == json.loads(response.data)
    dao_get_mock.assert_called_once_with(str(valid_id))


@pytest.mark.parametrize(
    'http_exception,http_status',
    [
        (NotFound, HTTPStatus.NOT_FOUND),
        (UnprocessableEntity, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
def test_get_time_entry_raise_http_exception(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    http_exception: HTTPException,
    http_status: tuple,
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    time_entries_dao.repository.find = Mock(side_effect=http_exception)

    response = client.get(
        f"/time-entries/{valid_id}",
        headers=valid_header,
        follow_redirects=True,
    )

    assert http_status == response.status_code
    time_entries_dao.repository.find.assert_called_once_with(valid_id, ANY)


def test_update_time_entry_calls_partial_update_with_incoming_payload(
    client: FlaskClient, mocker: MockFixture, valid_header: dict, valid_id: str
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    time_entries_dao.repository.partial_update = Mock(return_value={})

    time_entries_dao.repository.find = Mock(return_value={})
    time_entries_dao.check_whether_current_user_owns_item = Mock()

    response = client.put(
        f'/time-entries/{valid_id}',
        headers=valid_header,
        json=valid_time_entry_input,
        follow_redirects=True,
    )

    assert HTTPStatus.OK == response.status_code
    time_entries_dao.repository.partial_update.assert_called_once_with(
        valid_id, valid_time_entry_input, ANY
    )

    time_entries_dao.repository.find.assert_called_once()
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()


def test_update_time_entry_should_reject_bad_request(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    invalid_time_entry_data = valid_time_entry_input.copy()
    invalid_time_entry_data.update(
        {"project_id": fake.pyint(min_value=1, max_value=100)}
    )
    repository_update_mock = mocker.patch.object(
        time_entries_dao.repository, 'update', return_value=fake_time_entry
    )
    valid_id = fake.random_int(1, 9999)

    response = client.put(
        "/time-entries/%s" % valid_id,
        headers=valid_header,
        json=invalid_time_entry_data,
        follow_redirects=True,
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_update_mock.assert_not_called()


def test_update_time_entry_raise_not_found(
    client: FlaskClient, mocker: MockFixture, valid_header: dict, valid_id: str
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )
    from werkzeug.exceptions import NotFound

    time_entries_dao.repository.partial_update = Mock(side_effect=NotFound)

    time_entries_dao.repository.find = Mock(return_value={})
    time_entries_dao.check_whether_current_user_owns_item = Mock()

    response = client.put(
        f'/time-entries/{valid_id}',
        headers=valid_header,
        json=valid_time_entry_input,
        follow_redirects=True,
    )

    assert HTTPStatus.NOT_FOUND == response.status_code
    time_entries_dao.repository.partial_update.assert_called_once_with(
        valid_id, valid_time_entry_input, ANY
    )

    time_entries_dao.repository.find.assert_called_once()
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()


def test_delete_time_entry_calls_delete(
    client: FlaskClient, mocker: MockFixture, valid_header: dict, valid_id: str
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    time_entries_dao.repository.delete = Mock(return_value=None)
    time_entries_dao.repository.find = Mock()
    time_entries_dao.check_whether_current_user_owns_item = Mock()
    response = client.delete(
        f'/time-entries/{valid_id}',
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.NO_CONTENT == response.status_code
    assert b'' == response.data
    time_entries_dao.repository.delete.assert_called_once_with(valid_id, ANY)
    time_entries_dao.repository.find.assert_called_once()
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()


@pytest.mark.parametrize(
    'http_exception,http_status',
    [
        (NotFound, HTTPStatus.NOT_FOUND),
        (UnprocessableEntity, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
def test_delete_time_entry_raise_http_exception(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    http_exception: HTTPException,
    http_status: tuple,
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    time_entries_dao.repository.delete = Mock(side_effect=http_exception)
    time_entries_dao.repository.find = Mock()
    time_entries_dao.check_whether_current_user_owns_item = Mock()

    response = client.delete(
        f"/time-entries/{valid_id}",
        headers=valid_header,
        follow_redirects=True,
    )

    assert http_status == response.status_code
    time_entries_dao.repository.delete.assert_called_once_with(valid_id, ANY)
    time_entries_dao.repository.find.assert_called_once()
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()


def test_stop_time_entry_calls_partial_update(
    client: FlaskClient, mocker: MockFixture, valid_header: dict, valid_id: str
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    time_entries_dao.repository.partial_update = Mock(return_value={})

    time_entries_dao.repository.find = Mock(return_value={})
    time_entries_dao.check_time_entry_is_not_stopped = Mock()
    time_entries_dao.check_whether_current_user_owns_item = Mock()

    response = client.post(
        f'/time-entries/{valid_id}/stop',
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.OK == response.status_code
    time_entries_dao.repository.partial_update.assert_called_once_with(
        valid_id, {"end_date": ANY}, ANY
    )
    time_entries_dao.check_time_entry_is_not_stopped.assert_called_once()
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()


def test_stop_time_entry_raise_unprocessable_entity(
    client: FlaskClient, mocker: MockFixture, valid_header: dict, valid_id: str
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )
    from werkzeug.exceptions import UnprocessableEntity

    time_entries_dao.repository.partial_update = Mock(
        side_effect=UnprocessableEntity
    )

    time_entries_dao.repository.find = Mock(return_value={})
    time_entries_dao.check_time_entry_is_not_stopped = Mock()
    time_entries_dao.check_whether_current_user_owns_item = Mock()
    response = client.post(
        f'/time-entries/{valid_id}/stop',
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    time_entries_dao.repository.partial_update.assert_called_once_with(
        valid_id, {"end_date": ANY}, ANY
    )
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()
    time_entries_dao.check_time_entry_is_not_stopped.assert_called_once()


def test_restart_time_entry_calls_partial_update(
    client: FlaskClient, mocker: MockFixture, valid_header: dict, valid_id: str
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    time_entries_dao.repository.partial_update = Mock(return_value={})

    time_entries_dao.repository.find = Mock(return_value={})
    time_entries_dao.check_time_entry_is_not_started = Mock()
    time_entries_dao.check_whether_current_user_owns_item = Mock()

    response = client.post(
        f'/time-entries/{valid_id}/restart',
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.OK == response.status_code
    time_entries_dao.repository.partial_update.assert_called_once_with(
        valid_id, {"end_date": None}, ANY
    )
    time_entries_dao.check_time_entry_is_not_started.assert_called_once()
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()


def test_restart_time_entry_raise_unprocessable_entity(
    client: FlaskClient, mocker: MockFixture, valid_header: dict, valid_id: str
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )
    from werkzeug.exceptions import UnprocessableEntity

    time_entries_dao.repository.partial_update = Mock(
        side_effect=UnprocessableEntity
    )

    time_entries_dao.repository.find = Mock(return_value={})
    time_entries_dao.check_time_entry_is_not_started = Mock()
    time_entries_dao.check_whether_current_user_owns_item = Mock()

    response = client.post(
        f'/time-entries/{valid_id}/restart',
        headers=valid_header,
        follow_redirects=True,
    )

    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code
    time_entries_dao.repository.partial_update.assert_called_once_with(
        valid_id, {"end_date": None}, ANY
    )
    time_entries_dao.check_time_entry_is_not_started.assert_called_once()
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()


def test_get_running_should_call_find_running(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    tenant_id: str,
    owner_id: str,
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    repository_update_mock = mocker.patch.object(
        time_entries_dao.repository,
        'find_running',
        return_value=fake_time_entry,
    )
    time_entries_dao.stop_time_entry_if_was_left_running = Mock()

    response = client.get(
        "/time-entries/running", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    assert json.loads(response.data) is not None
    repository_update_mock.assert_called_once_with(tenant_id, owner_id)


def test_get_running_should_return_not_found_if_StopIteration(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    tenant_id: str,
    owner_id: str,
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    repository_update_mock = mocker.patch.object(
        time_entries_dao.repository, 'find_running', side_effect=StopIteration
    )

    response = client.get(
        "/time-entries/running", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.NOT_FOUND == response.status_code
    repository_update_mock.assert_called_once_with(tenant_id, owner_id)


@pytest.mark.parametrize(
    'invalid_uuid',
    ["zxy", "zxy%s" % fake.uuid4(), "%szxy" % fake.uuid4(), "  "],
)
def test_create_with_invalid_uuid_format_should_return_bad_request(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    invalid_uuid: str,
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    repository_container_create_item_mock = mocker.patch.object(
        time_entries_dao.repository.container,
        'create_item',
        return_value=fake_time_entry,
    )
    invalid_time_entry_input = {
        "project_id": fake.uuid4(),
        "activity_id": invalid_uuid,
    }
    response = client.post(
        "/time-entries",
        headers=valid_header,
        json=invalid_time_entry_input,
        follow_redirects=True,
    )

    assert HTTPStatus.BAD_REQUEST == response.status_code
    repository_container_create_item_mock.assert_not_called()


@pytest.mark.parametrize('valid_uuid', ["", fake.uuid4()])
def test_create_with_valid_uuid_format_should_return_created(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_uuid: str,
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    repository_container_create_item_mock = mocker.patch.object(
        time_entries_dao.repository.container,
        'create_item',
        return_value=fake_time_entry,
    )
    invalid_time_entry_input = {
        "project_id": fake.uuid4(),
        "activity_id": valid_uuid,
    }
    response = client.post(
        "/time-entries",
        headers=valid_header,
        json=invalid_time_entry_input,
        follow_redirects=True,
    )

    assert HTTPStatus.CREATED == response.status_code
    repository_container_create_item_mock.assert_called()


@pytest.mark.parametrize(
    'url,month,year',
    [
        ('/time-entries?month=4&year=2020', 4, 2020),
        ('/time-entries?month=4', 4, get_current_year()),
        ('/time-entries', get_current_month(), get_current_year()),
    ],
)
def test_find_all_is_called_with_generated_dates(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    owner_id: str,
    url: str,
    month: int,
    year: int,
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    dao_get_all_mock = mocker.patch.object(
        time_entries_dao, 'get_all', return_value=[]
    )

    response = client.get(url, headers=valid_header, follow_redirects=True)

    assert HTTPStatus.OK == response.status_code
    assert json.loads(response.data) is not None
    dao_get_all_mock.assert_called_once()


def test_summary_is_called_with_date_range_from_worked_time_module(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    owner_id: str,
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    worked_time.date_range = Mock(return_value=worked_time.date_range())
    repository_find_all_mock = mocker.patch.object(
        time_entries_dao.repository, 'find_all', return_value=[]
    )

    response = client.get(
        '/time-entries/summary', headers=valid_header, follow_redirects=True
    )

    date_range = worked_time.date_range()
    conditions = {'owner_id': owner_id}

    assert HTTPStatus.OK == response.status_code
    assert json.loads(response.data) is not None
    repository_find_all_mock.assert_called_once_with(
        ANY, conditions=conditions, date_range=date_range
    )
