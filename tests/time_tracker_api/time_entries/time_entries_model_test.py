import pytest
from faker import Faker

from commons.data_access_layer.database import EventContext
from time_tracker_api.time_entries.time_entries_model import (
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
        colliding_result = time_entry_repository.find_interception_with_date_range(
            start_date, end_date, owner_id, tenant_id
        )

        non_colliding_result = time_entry_repository.find_interception_with_date_range(
            start_date,
            end_date,
            owner_id,
            tenant_id,
            ignore_id=existing_item.id,
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
