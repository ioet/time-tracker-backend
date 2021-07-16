from http import HTTPStatus
from unittest.mock import Mock, patch
import pytest
from faker import Faker

from commons.data_access_layer.cosmos_db import CustomError
from commons.data_access_layer.database import EventContext
from time_tracker_api.time_entries.time_entries_repository import (
    TimeEntryCosmosDBRepository,
    TimeEntryCosmosDBModel,
)


def test_find_interception_with_date_range_should_return_true_if_there_are_collisions():
    owner_id = Faker().uuid4()
    tenant_id = Faker().uuid4()
    entry_start_date = "2020-10-01T05:00:00.000Z"
    entry_end_date = "2020-10-01T10:00:00.000Z"

    collision_entry = {
        "project_id": Faker().uuid4(),
        "activity_id": Faker().uuid4(),
        "description": Faker().paragraph(nb_sentences=2),
        "start_date": entry_start_date,
        "end_date": entry_end_date,
        "owner_id": Faker().uuid4(),
        "tenant_id": tenant_id,
    }
    time_entry_repository = TimeEntryCosmosDBRepository()
    query_items_mock = Mock(return_value=[collision_entry])
    time_entry_repository.container = Mock()
    time_entry_repository.container.query_items = query_items_mock

    exist_collision_entries = (
        time_entry_repository.find_interception_with_date_range(
            start_date=entry_start_date,
            end_date=entry_end_date,
            owner_id=owner_id,
            tenant_id=tenant_id,
        )
    )
    assert exist_collision_entries is True


def test_find_interception_with_date_range_should_return_false_if_there_are_not_collisions():
    entry_start_date = "2020-10-01T05:00:00.000Z"
    entry_end_date = "2020-10-01T10:00:00.000Z"

    time_entry_repository = TimeEntryCosmosDBRepository()
    query_items_mock = Mock(return_value=[])
    time_entry_repository.container = Mock()
    time_entry_repository.container.query_items = query_items_mock

    exist_collision_entries = (
        time_entry_repository.find_interception_with_date_range(
            start_date=entry_start_date,
            end_date=entry_end_date,
            owner_id=Faker().uuid4(),
            tenant_id=Faker().uuid4(),
        )
    )
    assert exist_collision_entries is False


def test_find_running_should_return_running_time_entry(
    running_time_entry, time_entry_repository: TimeEntryCosmosDBRepository
):
    found_time_entry = time_entry_repository.find_running(
        running_time_entry.tenant_id, running_time_entry.owner_id
    )

    assert found_time_entry is not None
    assert found_time_entry.id == running_time_entry.id
    assert found_time_entry.owner_id == running_time_entry.owner_id


def test_find_running_should_not_find_any_item(
    tenant_id: str,
    owner_id: str,
    time_entry_repository: TimeEntryCosmosDBRepository,
):
    with pytest.raises(CustomError) as custom_error:
        time_entry_repository.find_running(tenant_id, owner_id)

    assert custom_error.value.code == HTTPStatus.NO_CONTENT


@patch(
    'commons.data_access_layer.cosmos_db.CosmosDBRepository.on_update',
    new_callable=Mock,
)
def test_updated_item_with_deleted_key_should_not_call_validate_data(
    on_update_mock,
    event_context: EventContext,
    time_entry_repository: TimeEntryCosmosDBRepository,
):

    time_entry_repository.validate_data = Mock()
    time_entry_repository.replace_empty_value_per_none = Mock()
    time_entry_repository.on_update({'deleted': '01234'}, event_context)
    on_update_mock.assert_called_once()
    time_entry_repository.validate_data.assert_not_called()


@patch(
    'commons.data_access_layer.cosmos_db.CosmosDBRepository.on_update',
    new_callable=Mock,
)
def test_updated_item_without_deleted_key_should_call_validate_data(
    on_update_mock,
    event_context: EventContext,
    time_entry_repository: TimeEntryCosmosDBRepository,
):

    time_entry_repository.validate_data = Mock()
    time_entry_repository.replace_empty_value_per_none = Mock()
    time_entry_repository.on_update({}, event_context)
    on_update_mock.assert_called_once()
    time_entry_repository.validate_data.assert_called_once()


@patch(
    'time_tracker_api.time_entries.time_entries_repository.TimeEntryCosmosDBRepository.find_partition_key_value'
)
@patch(
    'time_tracker_api.time_entries.time_entries_repository.TimeEntryCosmosDBRepository.get_page_size_or'
)
@patch(
    'commons.data_access_layer.cosmos_db.CosmosDBRepository.generate_params'
)
@patch(
    'time_tracker_api.time_entries.time_entries_repository.TimeEntryCosmosDBRepository.add_complementary_info'
)
def test_find_all_time_entries_new_version(
    add_complementary_info_mock,
    generate_params_mock,
    get_page_size_or_mock,
    find_partition_key_value_mock,
    event_context: EventContext,
    time_entry_repository: TimeEntryCosmosDBRepository,
):
    expected_item = {
        'id': 'id',
        'start_date': '2021-03-22T10:00:00.000Z',
        'end_date': "2021-03-22T11:00:00.000Z",
        'description': 'do some testing',
        'tenant_id': 'tenant_id',
        'project_id': 'project_id',
        'activity_id': 'activity_id',
        'technologies': ['python'],
    }
    query_items_mock = Mock(return_value=[expected_item])
    time_entry_repository.container = Mock()
    time_entry_repository.container.query_items = query_items_mock

    time_entry_repository.add_complementary_info = query_items_mock

    result = time_entry_repository.find_all(
        conditions={"user_id": "*"},
        event_context=event_context,
        date_range={
            'start_date': "2021-03-22T10:00:00.000Z",
            'end_date': "2021-03-22T11:00:00.000Z",
        },
    )

    find_partition_key_value_mock.assert_called_once()
    get_page_size_or_mock.assert_called_once()

    assert len(result) == 1
    time_entry = result[0]
    assert time_entry == expected_item


@patch(
    'time_tracker_api.time_entries.time_entries_repository.TimeEntryCosmosDBRepository.find_partition_key_value'
)
def test_get_last_entry(
    find_partition_key_value_mock,
    event_context: EventContext,
    time_entry_repository: TimeEntryCosmosDBRepository,
):
    expected_item = {
        'id': 'id',
        'start_date': '2021-03-22T10:00:00.000Z',
        'end_date': "2021-03-22T11:00:00.000Z",
        'description': 'do some testing',
        'tenant_id': 'tenant_id',
        'project_id': 'project_id',
        'activity_id': 'activity_id',
        'technologies': ['python'],
    }
    query_items_mock = Mock(return_value=iter([expected_item]))
    time_entry_repository.container = Mock()
    time_entry_repository.container.query_items = query_items_mock

    time_entry = time_entry_repository.get_last_entry(
        'id1', ['id1'], event_context
    )

    find_partition_key_value_mock.assert_called_once()
    assert isinstance(time_entry, TimeEntryCosmosDBModel)
    assert time_entry.__dict__ == expected_item


expected_item = {
    'id': 'id',
    'owner_id': '1',
    'start_date': '2021-03-22T10:00:00.000Z',
    'end_date': "2021-03-22T11:00:00.000Z",
    'description': 'do some testing',
    'tenant_id': 'tenant_id',
    'project_id': 'project_id',
    'activity_id': 'activity_id',
    'technologies': ['python'],
}

running_item = {
    'id': 'id',
    'owner_id': '1',
    'id_running_entry': '1',
    'update_last_entry_if_overlap': True,
    'start_date': '2021-03-22T10:30:00.000Z',
    'end_date': '2021-03-22T11:30:00.000Z',
    'description': 'do some testing',
    'tenant_id': 'tenant_id',
    'project_id': 'project_id',
    'activity_id': 'activity_id',
    'technologies': ['python'],
}

last_item_update = {
    'id': 'id',
    'owner_id': '1',
    'start_date': '2021-03-22T10:00:00.000Z',
    'end_date': "2021-03-22T10:30:00.000Z",
    'description': 'do some testing',
    'tenant_id': 'tenant_id',
    'project_id': 'project_id',
    'activity_id': 'activity_id',
    'technologies': ['python'],
}


@pytest.mark.parametrize(
    "expected_item, running_item, last_item_update",
    [(expected_item, running_item, last_item_update)],
)
def test_update_last_entry(
    event_context: EventContext,
    time_entry_repository: TimeEntryCosmosDBRepository,
    expected_item,
    running_item,
    last_item_update,
):
    query_items_mock = Mock(return_value=iter([expected_item]))
    time_entry_repository.container = Mock()
    time_entry_repository.container.query_items = query_items_mock

    partial_update_mock = Mock(return_value=[last_item_update])
    time_entry_repository.partial_update = partial_update_mock

    time_entry_repository.update_last_entry(
        running_item.get('owner_id'),
        running_item.get('start_date'),
        running_item.get('id_running_entry'),
        event_context,
    )

    partial_update_mock.assert_called_once()
    query_items_mock.assert_called_once()
