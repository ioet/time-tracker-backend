import pytest

from time_tracker.time_entries._infrastructure import TimeEntriesSQLDao

from time_tracker._infrastructure import DB


@pytest.fixture(name='create_time_entry_fake_dao')
def _create_fake_dao() -> TimeEntriesSQLDao:
    db_fake = DB('sqlite:///:memory:')
    dao = TimeEntriesSQLDao(db_fake)
    return dao


def test_update__returns_an_time_entry_dto__when_found_one_time_entry_to_update(
    create_time_entry_fake_dao, time_entry_factory, insert_activity, activity_factory
):
    dao = create_time_entry_fake_dao
    inserted_activity = insert_activity(activity_factory(), dao.db)
    existent_time_entries = time_entry_factory(activity_id=inserted_activity.id, technologies="[jira,sql]")
    inserted_time_entries = dao.create(existent_time_entries).__dict__
    time_entry_id = inserted_time_entries["id"]
    inserted_time_entries.update({"description": "description updated"})

    time_entry = dao.update(time_entry_id=time_entry_id, time_entry_data=inserted_time_entries)

    assert time_entry.id == time_entry_id
    assert time_entry.description == "description updated"


def test_update__returns_none__when_doesnt_found_one_time_entry_to_update(
     create_time_entry_fake_dao, time_entry_factory, insert_activity, activity_factory
):
    dao = create_time_entry_fake_dao
    inserted_activity = insert_activity(activity_factory(), dao.db)
    existent_time_entries = time_entry_factory(activity_id=inserted_activity.id, technologies="[jira,sql]")
    inserted_time_entries = dao.create(existent_time_entries).__dict__

    time_entry = dao.update(0, inserted_time_entries)

    assert time_entry is None
