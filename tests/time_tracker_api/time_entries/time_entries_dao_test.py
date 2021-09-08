from unittest.mock import ANY

from time_tracker_api.database import APICosmosDBDao
from time_tracker_api.time_entries.time_entries_repository import (
    TimeEntryCosmosDBRepository,
)


def test_get_latest_entries_must_be_called_with_default_amount_of_entries(
    mocker, time_entries_dao
):
    expected_conditions = {'owner_id': ANY}

    expected_entries_amount = 20

    time_entries_repository_find_all_mock = mocker.patch.object(
        TimeEntryCosmosDBRepository, 'find_all'
    )
    mocker.patch.object(APICosmosDBDao, 'create_event_context')

    time_entries_dao.get_latest_entries()

    time_entries_repository_find_all_mock.assert_called_with(
        conditions=expected_conditions,
        max_count=expected_entries_amount,
        event_context=ANY,
    )


def test_get_latest_entries_must_be_called_with_amount_of_entries_passed_in_condition(
    mocker, time_entries_dao
):
    time_entries_repository_find_all_mock = mocker.patch.object(
        TimeEntryCosmosDBRepository, 'find_all'
    )
    mocker.patch.object(APICosmosDBDao, 'create_event_context')

    expected_entries_amount = 40
    conditions = {'limit': expected_entries_amount}

    time_entries_dao.get_latest_entries(conditions=conditions)

    conditions.update({'owner_id': ANY})

    time_entries_repository_find_all_mock.assert_called_with(
        conditions=conditions,
        max_count=expected_entries_amount,
        event_context=ANY,
    )
