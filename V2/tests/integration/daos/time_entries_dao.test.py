import json
import pytest
import typing

from faker import Faker

from time_tracker.time_entries._infrastructure import TimeEntriesJsonDao
from time_tracker.time_entries._domain import TimeEntry


@pytest.fixture(name="create_fake_time_entries")
def _create_fake_time_entries(mocker) -> typing.List[TimeEntry]:
    def _creator(time_entries):
        read_data = json.dumps(time_entries)
        mocker.patch("builtins.open", mocker.mock_open(read_data=read_data))
        return [TimeEntry(**time_entry) for time_entry in time_entries]

    return _creator


def test_create_time_entry__returns_an_time_entry_dto__when_create_an_time_entry_that_matches_attributes(
    create_fake_time_entries, time_entry_factory
):
    create_fake_time_entries([])

    time_entries_json_dao = TimeEntriesJsonDao(Faker().file_path())
    time_entry_data = time_entry_factory()
    result = time_entries_json_dao.create(time_entry_data.__dict__)
    assert result == TimeEntry(**time_entry_data)


def test_delete__returns_an_time_entry_with_true_deleted__when_an_time_entry_matching_its_id_is_found(
    create_fake_time_entries, time_entry_factory
):
    time_entries_json_dao = TimeEntriesJsonDao(Faker().file_path())
    time_entries = create_fake_time_entries(
        [
            time_entry_factory().__dict__
        ]
    )

    time_entry_dto = time_entries[0]
    result = time_entries_json_dao.delete(time_entry_dto.id)

    assert result.deleted is True


def test_delete__returns_none__when_no_time_entry_matching_its_id_is_found(
    create_fake_time_entries,
):
    time_entries_json_dao = TimeEntriesJsonDao(Faker().file_path())
    create_fake_time_entries([])

    result = time_entries_json_dao.delete(Faker().pyint())

    assert result is None
