from unittest.mock import Mock, patch
import pytest
from faker import Faker

from commons.data_access_layer.database import EventContext
from time_tracker_api.time_entries.time_entries_model import (
    TimeEntryCosmosDBModel,
)
from time_tracker_api.time_entries.time_entries_repository import (
    TimeEntryCosmosDBRepository,
    TimeEntryCosmosDBModel,
)


def create_time_entry(
    start_date: str,
    end_date: str,
    owner_id: str,
    tenant_id: str,
    event_context: EventContext,
    time_entry_repository: TimeEntryCosmosDBRepository,
) -> TimeEntryCosmosDBModel:
    data = {
        "project_id": Faker().uuid4(),
        "activity_id": Faker().uuid4(),
        "description": Faker().paragraph(nb_sentences=2),
        "start_date": start_date,
        "end_date": end_date,
        "owner_id": owner_id,
        "tenant_id": tenant_id,
    }

    created_item = time_entry_repository.create(
        data, event_context, mapper=TimeEntryCosmosDBModel
    )
    return created_item


@pytest.mark.parametrize(
    'start_date,end_date,start_date_,end_date_',
    [
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
        ),
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T07:00:00.000Z",
            "2020-10-01T12:00:00.000Z",
        ),
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T02:00:00.000Z",
            "2020-10-01T07:00:00.000Z",
        ),
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T02:00:00.000Z",
            "2020-10-01T12:00:00.000Z",
        ),
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T06:00:00.000Z",
            "2020-10-01T07:00:00.000Z",
        ),
    ],
)
def test_find_interception_with_date_range_should_find(
    start_date: str,
    end_date: str,
    start_date_: str,
    end_date_: str,
    owner_id: str,
    tenant_id: str,
    time_entry_repository: TimeEntryCosmosDBRepository,
    event_context: EventContext,
):
    existing_item = create_time_entry(
        start_date,
        end_date,
        owner_id,
        tenant_id,
        event_context,
        time_entry_repository,
    )

    try:
        result = time_entry_repository.find_interception_with_date_range(
            start_date_, end_date_, owner_id, tenant_id
        )

        assert result is not None
        assert len(result) > 0
        assert any([existing_item.id == item.id for item in result])
    finally:
        time_entry_repository.delete_permanently(
            existing_item.id, event_context
        )


@pytest.mark.parametrize(
    'start_date,end_date,start_date_,end_date_',
    [
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T15:00:00.000Z",
        ),
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T12:00:00.000Z",
            "2020-10-01T15:00:00.000Z",
        ),
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T02:00:00.000Z",
            "2020-10-01T05:00:00.000Z",
        ),
        (
            "2020-10-01T05:00:00.000Z",
            "2020-10-01T10:00:00.000Z",
            "2020-10-01T02:00:00.000Z",
            "2020-10-01T04:00:00.000Z",
        ),
    ],
)
def test_find_interception_with_date_range_should_not_find(
    start_date: str,
    end_date: str,
    start_date_: str,
    end_date_: str,
    owner_id: str,
    tenant_id: str,
    time_entry_repository: TimeEntryCosmosDBRepository,
    event_context: EventContext,
):
    existing_item = create_time_entry(
        start_date,
        end_date,
        owner_id,
        tenant_id,
        event_context,
        time_entry_repository,
    )

    try:
        result = time_entry_repository.find_interception_with_date_range(
            start_date_, end_date_, owner_id, tenant_id
        )

        assert result == []
        assert len(result) == 0
        assert not any([existing_item.id == item.id for item in result])
    finally:
        time_entry_repository.delete_permanently(
            existing_item.id, event_context
        )


def test_find_interception_should_ignore_id_of_existing_item(
    owner_id: str,
    tenant_id: str,
    time_entry_repository: TimeEntryCosmosDBRepository,
    event_context: EventContext,
):
    start_date = "2020-10-01T05:00:00.000Z"
    end_date = "2020-10-01T10:00:00.000Z"
    existing_item = create_time_entry(
        start_date,
        end_date,
        owner_id,
        tenant_id,
        event_context,
        time_entry_repository,
    )

    try:
        colliding_result = (
            time_entry_repository.find_interception_with_date_range(
                start_date, end_date, owner_id, tenant_id
            )
        )

        non_colliding_result = (
            time_entry_repository.find_interception_with_date_range(
                start_date,
                end_date,
                owner_id,
                tenant_id,
                ignore_id=existing_item.id,
            )
        )

        assert colliding_result is not None
        assert any([existing_item.id == item.id for item in colliding_result])
        assert non_colliding_result is not None
        assert not any(
            [existing_item.id == item.id for item in non_colliding_result]
        )
    finally:
        time_entry_repository.delete_permanently(
            existing_item.id, event_context
        )


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
    try:
        time_entry_repository.find_running(tenant_id, owner_id)
    except Exception as e:
        assert type(e) is StopIteration


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
def test_find_all_v2(
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

    result = time_entry_repository.find_all_v2(
        event_context,
        ['owner_id'],
        {
            'start_date': "2021-03-22T10:00:00.000Z",
            'end_date': "2021-03-22T11:00:00.000Z",
        },
    )

    find_partition_key_value_mock.assert_called_once()
    get_page_size_or_mock.assert_called_once()
    assert len(result) == 1
    time_entry = result[0]
    assert isinstance(time_entry, TimeEntryCosmosDBModel)
    assert time_entry.__dict__ == expected_item


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
    query_items_mock = Mock(return_value=[expected_item])
    time_entry_repository.container = Mock()
    time_entry_repository.container.query_items = query_items_mock

    result = time_entry_repository.get_last_entry('id1', event_context)
    find_partition_key_value_mock.assert_called_once()

    assert len(result) == 1
    time_entry = result.pop()
    assert isinstance(time_entry, TimeEntryCosmosDBModel)
    assert time_entry.__dict__ == expected_item
