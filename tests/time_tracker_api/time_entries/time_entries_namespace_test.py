from datetime import timedelta
from unittest.mock import ANY, Mock, patch

from faker import Faker
from flask import json
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture, pytest

from utils.time import (
    get_current_year,
    get_current_month,
    current_datetime,
    current_datetime_str,
    get_date_range_of_month,
    datetime_str,
)
from utils import worked_time
from time_tracker_api.time_entries.time_entries_model import (
    TimeEntryCosmosDBModel,
)

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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    time_entries_dao,
):
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


@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_azure_app_configuration_client'
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.is_toggle_enabled_for_user'
)
def test_list_all_time_entries(
    is_toggle_enabled_for_user_mock,
    get_azure_app_configuration_client_mock,
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    time_entries_dao,
):
    is_toggle_enabled_for_user_mock.return_value = True

    dao_get_all_mock = mocker.patch.object(
        time_entries_dao, 'get_all', return_value=[]
    )

    response = client.get(
        "/time-entries", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    dao_get_all_mock.assert_called_once()


def test_list_last_time_entries(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    from time_tracker_api.time_entries.time_entries_namespace import (
        time_entries_dao,
    )

    dao_get_all_mock = mocker.patch.object(
        time_entries_dao, 'get_lastest_entries_by_project', return_value=[]
    )

    response = client.get(
        "/time-entries/latest", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    dao_get_all_mock.assert_called_once()


def test_get_time_entry_should_succeed_with_valid_id(
    client: FlaskClient, mocker: MockFixture, valid_header: dict
):
    dao_get_all_mock = mocker.patch.object(
        time_entries_dao, 'get_lastest_entries_by_project', return_value=[]
    )

    response = client.get(
        "/time-entries/latest", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    assert [] == json.loads(response.data)
    dao_get_all_mock.assert_called_once()


@patch(
    'time_tracker_api.time_entries.time_entries_dao.TimeEntriesCosmosDBDao.create_event_context',
    Mock(),
)
@patch(
    'time_tracker_api.time_entries.time_entries_dao.TimeEntriesCosmosDBDao.build_custom_query',
    Mock(),
)
@patch(
    'time_tracker_api.time_entries.time_entries_dao.TimeEntriesCosmosDBDao.handle_date_filter_args',
    Mock(),
)
@patch(
    'time_tracker_api.time_entries.time_entries_repository.TimeEntryCosmosDBRepository.create_sql_date_range_filter',
    Mock(),
)
@patch(
    'commons.data_access_layer.cosmos_db.CosmosDBRepository.generate_params',
    Mock(),
)
@patch('msal.ConfidentialClientApplication', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.is_test_user')
@patch('utils.azure_users.AzureConnection.get_test_user_ids')
@pytest.mark.parametrize(
    'current_user_is_tester, expected_user_ids',
    [
        (True, ['id1', 'id1']),
    ],
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_azure_app_configuration_client'
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.is_toggle_enabled_for_user'
)
def test_get_time_entries_by_type_of_user_when_is_user_tester(
    is_toggle_enabled_for_user_mock,
    get_azure_app_configuration_client_mock,
    get_test_user_ids_mock,
    is_test_user_mock,
    client: FlaskClient,
    valid_header: dict,
    time_entries_dao,
    current_user_is_tester,
    expected_user_ids,
):
    is_toggle_enabled_for_user_mock.return_value = True
    test_user_id = "id1"
    non_test_user_id = "id2"
    te1 = TimeEntryCosmosDBModel(
        {
            "id": '1',
            "project_id": "1",
            "owner_id": test_user_id,
            "tenant_id": '1',
            "start_date": "",
        }
    )
    te2 = TimeEntryCosmosDBModel(
        {
            "id": '2',
            "project_id": "2",
            "owner_id": test_user_id,
            "tenant_id": '2',
            "start_date": "",
        }
    )

    find_all_mock = Mock()
    find_all_mock.return_value = [te1, te2]

    time_entries_dao.repository.find_all = find_all_mock

    is_test_user_mock.return_value = current_user_is_tester

    response = client.get(
        "/time-entries?user_id=*", headers=valid_header, follow_redirects=True
    )

    get_test_user_ids_mock.assert_not_called()
    find_all_mock.assert_called()

    expected_user_ids_in_time_entries = expected_user_ids
    actual_user_ids_in_time_entries = [
        time_entry["owner_id"] for time_entry in json.loads(response.data)
    ]
    assert expected_user_ids_in_time_entries == actual_user_ids_in_time_entries


@patch(
    'time_tracker_api.time_entries.time_entries_dao.TimeEntriesCosmosDBDao.create_event_context',
    Mock(),
)
@patch(
    'time_tracker_api.time_entries.time_entries_dao.TimeEntriesCosmosDBDao.build_custom_query',
    Mock(),
)
@patch(
    'time_tracker_api.time_entries.time_entries_dao.TimeEntriesCosmosDBDao.handle_date_filter_args',
    Mock(),
)
@patch(
    'time_tracker_api.time_entries.time_entries_repository.TimeEntryCosmosDBRepository.create_sql_date_range_filter',
    Mock(),
)
@patch(
    'commons.data_access_layer.cosmos_db.CosmosDBRepository.generate_params',
    Mock(),
)
@patch('msal.ConfidentialClientApplication', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch('utils.azure_users.AzureConnection.is_test_user')
@patch('utils.azure_users.AzureConnection.get_test_user_ids')
@pytest.mark.parametrize(
    'current_user_is_tester, expected_user_ids',
    [
        (False, ['id1', 'id1']),
    ],
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_azure_app_configuration_client'
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.is_toggle_enabled_for_user'
)
def test_get_time_entries_by_type_of_user_when_is_not_user_tester(
    is_toggle_enabled_for_user_mock,
    get_azure_app_configuration_client_mock,
    get_test_user_ids_mock,
    is_test_user_mock,
    client: FlaskClient,
    valid_header: dict,
    time_entries_dao,
    current_user_is_tester,
    expected_user_ids,
):
    is_toggle_enabled_for_user_mock.return_value = True
    test_user_id = "id1"
    non_test_user_id = "id2"
    te1 = TimeEntryCosmosDBModel(
        {
            "id": '1',
            "project_id": "1",
            "owner_id": test_user_id,
            "tenant_id": '1',
            "start_date": "",
        }
    )
    te2 = TimeEntryCosmosDBModel(
        {
            "id": '2',
            "project_id": "2",
            "owner_id": test_user_id,
            "tenant_id": '2',
            "start_date": "",
        }
    )

    find_all_mock = Mock()
    find_all_mock.return_value = [te1, te2]

    time_entries_dao.repository.find_all = find_all_mock

    is_test_user_mock.return_value = current_user_is_tester
    get_test_user_ids_mock.return_value = [test_user_id]

    response = client.get(
        "/time-entries?user_id=*", headers=valid_header, follow_redirects=True
    )

    get_test_user_ids_mock.assert_called()
    find_all_mock.assert_called()

    expected_user_ids_in_time_entries = expected_user_ids
    actual_user_ids_in_time_entries = [
        time_entry["owner_id"] for time_entry in json.loads(response.data)
    ]
    assert expected_user_ids_in_time_entries == actual_user_ids_in_time_entries


def test_get_time_entry_should_succeed_with_valid_id(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    time_entries_dao,
):
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
    time_entries_dao,
):
    time_entries_dao.repository.find = Mock(side_effect=http_exception)

    response = client.get(
        f"/time-entries/{valid_id}",
        headers=valid_header,
        follow_redirects=True,
    )

    assert http_status == response.status_code
    time_entries_dao.repository.find.assert_called_once_with(valid_id, ANY)


def test_update_time_entry_calls_partial_update_with_incoming_payload(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    time_entries_dao,
):
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
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    time_entries_dao,
):
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
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    time_entries_dao,
):
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
    time_entries_dao,
):
    repository_update_mock = mocker.patch.object(
        time_entries_dao.repository,
        'find_running',
        return_value=fake_time_entry,
    )

    response = client.get(
        "/time-entries/running", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.OK == response.status_code
    assert json.loads(response.data) is not None
    repository_update_mock.assert_called_once_with(tenant_id, owner_id)


def test_get_running_should_return_no_content_if_StopIteration(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    tenant_id: str,
    owner_id: str,
    time_entries_dao,
):
    repository_update_mock = mocker.patch.object(
        time_entries_dao.repository, 'find_running', side_effect=StopIteration
    )

    response = client.get(
        "/time-entries/running", headers=valid_header, follow_redirects=True
    )

    assert HTTPStatus.NO_CONTENT == response.status_code
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
    time_entries_dao,
):
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
    time_entries_dao,
):
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


@patch('msal.ConfidentialClientApplication', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch(
    'utils.azure_users.AzureConnection.is_test_user', Mock(return_value=True)
)
@pytest.mark.parametrize(
    'url',
    [
        (
            '/time-entries?start_date=2020-04-01T00:00:00&end_date=2020-04-30T23:00:00'
        ),
        ('/time-entries?month=4&year=2020'),
        ('/time-entries?month=4'),
        ('/time-entries?year=2020'),
        ('/time-entries'),
    ],
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_azure_app_configuration_client'
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.is_toggle_enabled_for_user'
)
def test_get_all_passes_date_range_built_from_params_to_find_all(
    is_toggle_enabled_for_user_mock,
    get_azure_app_configuration_client_mock,
    client: FlaskClient,
    valid_header: dict,
    url: str,
    time_entries_dao,
):
    is_toggle_enabled_for_user_mock.return_value = True
    time_entries_dao.repository.find_all = Mock(return_value=[])

    response = client.get(url, headers=valid_header)

    time_entries_dao.repository.find_all.assert_called_once()
    _, kwargs = time_entries_dao.repository.find_all.call_args
    assert 'date_range' in kwargs
    assert 'start_date' in kwargs['date_range']
    assert 'end_date' in kwargs['date_range']


@patch('msal.ConfidentialClientApplication', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch(
    'utils.azure_users.AzureConnection.is_test_user', Mock(return_value=True)
)
@pytest.mark.parametrize(
    'url,start_date,end_date',
    [
        (
            '/time-entries?month=4&year=2020',
            '2020-04-01T05:00:00+00:00',
            '2020-05-01T04:59:59.999999+00:00',
        ),
        (
            '/time-entries?start_date=2020-04-01T00:00:00&end_date=2020-04-30T23:00:00',
            '2020-04-01T05:00:00+00:00',
            '2020-05-01T04:00:00+00:00',
        ),
    ],
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_azure_app_configuration_client'
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.is_toggle_enabled_for_user'
)
def test_get_all_passes_date_range_to_find_all_with_default_tz_offset(
    is_toggle_enabled_for_user_mock,
    get_azure_app_configuration_client_mock,
    client: FlaskClient,
    valid_header: dict,
    time_entries_dao,
    url: str,
    start_date: str,
    end_date: str,
):
    is_toggle_enabled_for_user_mock.return_value = True

    time_entries_dao.repository.find_all = Mock(return_value=[])

    response = client.get(url, headers=valid_header)

    time_entries_dao.repository.find_all.assert_called_once()
    _, kwargs = time_entries_dao.repository.find_all.call_args
    assert 'date_range' in kwargs
    assert 'start_date' in kwargs['date_range']
    assert 'end_date' in kwargs['date_range']
    assert kwargs['date_range']['start_date'] == start_date
    assert kwargs['date_range']['end_date'] == end_date


@patch('msal.ConfidentialClientApplication', Mock())
@patch('utils.azure_users.AzureConnection.get_token', Mock())
@patch(
    'utils.azure_users.AzureConnection.is_test_user', Mock(return_value=True)
)
@pytest.mark.parametrize(
    'url,start_date,end_date',
    [
        (
            '/time-entries?month=4&year=2020&timezone_offset=300',
            '2020-04-01T05:00:00+00:00',
            '2020-05-01T04:59:59.999999+00:00',
        ),
        (
            '/time-entries?start_date=2020-04-01T00:00:00&end_date=2020-04-30T23:00:00&timezone_offset=300',
            '2020-04-01T05:00:00+00:00',
            '2020-05-01T04:00:00+00:00',
        ),
        (
            '/time-entries?month=4&year=2020&timezone_offset=-120',
            '2020-03-31T22:00:00+00:00',
            '2020-04-30T21:59:59.999999+00:00',
        ),
        (
            '/time-entries?start_date=2020-04-01T00:00:00&end_date=2020-04-30T23:00:00&timezone_offset=-120',
            '2020-03-31T22:00:00+00:00',
            '2020-04-30T21:00:00+00:00',
        ),
        (
            '/time-entries?month=4&year=2020&timezone_offset=420',
            '2020-04-01T07:00:00+00:00',
            '2020-05-01T06:59:59.999999+00:00',
        ),
        (
            '/time-entries?start_date=2020-04-01T00:00:00&end_date=2020-04-30T23:00:00&timezone_offset=420',
            '2020-04-01T07:00:00+00:00',
            '2020-05-01T06:00:00+00:00',
        ),
    ],
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.get_azure_app_configuration_client'
)
@patch(
    'commons.feature_toggles.feature_toggle_manager.FeatureToggleManager.is_toggle_enabled_for_user'
)
def test_get_all_passes_date_range_to_find_all_with_given_tz_offset(
    is_toggle_enabled_for_user_mock,
    get_azure_app_configuration_client_mock,
    client: FlaskClient,
    valid_header: dict,
    time_entries_dao,
    url: str,
    start_date: str,
    end_date: str,
):
    is_toggle_enabled_for_user_mock.return_value = True
    time_entries_dao.repository.find_all = Mock(return_value=[])

    response = client.get(url, headers=valid_header)

    time_entries_dao.repository.find_all.assert_called_once()
    _, kwargs = time_entries_dao.repository.find_all.call_args
    assert 'date_range' in kwargs
    assert 'start_date' in kwargs['date_range']
    assert 'end_date' in kwargs['date_range']
    assert kwargs['date_range']['start_date'] == start_date
    assert kwargs['date_range']['end_date'] == end_date


def test_summary_is_called_with_date_range_from_worked_time_module(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    owner_id: str,
    time_entries_dao,
):
    worked_time.date_range = Mock(return_value=worked_time.date_range())
    repository_find_all_mock = mocker.patch.object(
        time_entries_dao.repository, 'find_all_entries', return_value=[]
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


def test_paginated_fails_with_no_params(
    client: FlaskClient,
    valid_header: dict,
):
    response = client.get('/time-entries/paginated', headers=valid_header)
    assert HTTPStatus.BAD_REQUEST == response.status_code


def test_paginated_succeeds_with_valid_params(
    client: FlaskClient,
    valid_header: dict,
):
    response = client.get(
        '/time-entries/paginated?start_date=2020-09-10T00:00:00-05:00&end_date=2020-09-10T23:59:59-05:00&timezone_offset=300&start=0&length=5',
        headers=valid_header,
    )
    assert HTTPStatus.OK == response.status_code


def test_paginated_response_contains_expected_props(
    client: FlaskClient,
    valid_header: dict,
):
    response = client.get(
        '/time-entries/paginated?start_date=2020-09-10T00:00:00-05:00&end_date=2020-09-10T23:59:59-05:00&timezone_offset=300&start=0&length=5',
        headers=valid_header,
    )
    assert 'data' in json.loads(response.data)
    assert 'records_total' in json.loads(response.data)


def test_paginated_sends_max_count_and_offset_on_call_to_repository(
    client: FlaskClient, valid_header: dict, time_entries_dao
):
    time_entries_dao.repository.find_all = Mock(return_value=[])

    response = client.get(
        '/time-entries/paginated?start_date=2020-09-10T00:00:00-05:00&end_date=2020-09-10T23:59:59-05:00&timezone_offset=300&start=0&length=5',
        headers=valid_header,
    )

    time_entries_dao.repository.find_all.assert_called_once()

    _, kwargs = time_entries_dao.repository.find_all.call_args
    assert 'max_count' in kwargs and kwargs['max_count'] is not None
    assert 'offset' in kwargs and kwargs['offset'] is not None


def test_update_time_entry_calls_update_last_entry(
    client: FlaskClient,
    mocker: MockFixture,
    valid_header: dict,
    valid_id: str,
    time_entries_dao,
):
    time_entries_dao.repository.partial_update = Mock(return_value={})
    time_entries_dao.repository.find = Mock(return_value={})
    time_entries_dao.check_whether_current_user_owns_item = Mock()
    time_entries_dao.repository.update_last_entry = Mock(return_value={})

    update_time_entry = valid_time_entry_input.copy()
    update_time_entry['update_last_entry_if_overlap'] = True

    response = client.put(
        f'/time-entries/{valid_id}',
        headers=valid_header,
        json=update_time_entry,
        follow_redirects=True,
    )

    assert HTTPStatus.OK == response.status_code
    time_entries_dao.repository.partial_update.assert_called_once()
    time_entries_dao.repository.find.assert_called_once()
    time_entries_dao.check_whether_current_user_owns_item.assert_called_once()
    time_entries_dao.repository.update_last_entry.assert_called_once()
