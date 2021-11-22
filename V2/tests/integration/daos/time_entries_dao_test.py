import pytest
import typing

from faker import Faker

import time_tracker.time_entries._domain as domain
import time_tracker.time_entries._infrastructure as infrastructure
from time_tracker._infrastructure import DB


@pytest.fixture(name='create_fake_dao')
def _fake_dao() -> domain.TimeEntriesDao:
    def _create_fake_dao(db_fake: DB) -> domain.TimeEntriesDao:
        dao = infrastructure.TimeEntriesSQLDao(db_fake)
        return dao
    return _create_fake_dao


@pytest.fixture(name='clean_database', autouse=True)
def _clean_database():
    yield
    db_fake = DB()
    dao = infrastructure.TimeEntriesSQLDao(db_fake)
    query = dao.time_entry.delete()
    dao.db.get_session().execute(query)


def test__time_entry__returns_a_time_entry_dto__when_saves_correctly_with_sql_database(
    test_db, time_entry_factory, create_fake_dao, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)

    time_entry_to_insert = time_entry_factory(activity_id=inserted_activity.id)

    inserted_time_entry = dao.create(time_entry_to_insert)

    assert isinstance(inserted_time_entry, domain.TimeEntry)
    assert inserted_time_entry == time_entry_to_insert


def test__time_entry__returns_None__when_not_saves_correctly(
    time_entry_factory, create_fake_dao, test_db
):
    dao = create_fake_dao(test_db)
    time_entry_to_insert = time_entry_factory(activity_id=1203)

    inserted_time_entry = dao.create(time_entry_to_insert)

    assert inserted_time_entry is None


def test_delete__returns_an_time_entry_with_true_deleted__when_an_time_entry_matching_its_id_is_found(
    create_fake_dao, test_db, time_entry_factory, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)
    existent_time_entry = time_entry_factory(activity_id=inserted_activity.id)
    inserted_time_entry = dao.create(existent_time_entry)

    result = dao.delete(inserted_time_entry.id)

    assert result.deleted is True


def test_delete__returns_none__when_no_time_entry_matching_its_id_is_found(
    create_fake_dao, test_db
):
    dao = create_fake_dao(test_db)

    result = dao.delete(Faker().pyint())

    assert result is None


def test_update__returns_an_time_entry_dto__when_found_one_time_entry_to_update(
    test_db, create_fake_dao, time_entry_factory, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)
    existent_time_entries = time_entry_factory(activity_id=inserted_activity.id)
    inserted_time_entries = dao.create(existent_time_entries).__dict__
    time_entry_id = inserted_time_entries["id"]
    inserted_time_entries.update({"description": "description updated"})

    time_entry = dao.update(time_entry_id=time_entry_id, time_entry_data=inserted_time_entries)

    assert time_entry.id == time_entry_id
    assert time_entry.description == inserted_time_entries.get("description")


def test_update__returns_none__when_doesnt_found_one_time_entry_to_update(
    test_db, create_fake_dao, time_entry_factory, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)
    existent_time_entries = time_entry_factory(activity_id=inserted_activity.id)
    inserted_time_entries = dao.create(existent_time_entries).__dict__

    time_entry = dao.update(0, inserted_time_entries)

    assert time_entry is None


def test__get_all__returns_a_list_of_time_entries_dto_objects__when_one_or_more_time_entries_are_found_in_sql_database(
    test_db, create_fake_dao, time_entry_factory, insert_activity, activity_factory
):

    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id)
    inserted_time_entries = [dao.create(time_entries_to_insert)]

    time_entry = dao.get_all()

    assert isinstance(time_entry, typing.List)
    assert time_entry == inserted_time_entries


def test__get_all__returns_an_empty_list__when_doesnt_found_any_time_entries_in_sql_database(
    test_db, create_fake_dao, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    insert_activity(activity_factory(), dao.db)

    time_entry = dao.get_all()
    assert time_entry == []


def test__get_by_id__returns_a_time_entry_dto__when_found_one_time_entry_that_match_id_with_sql_database(
    test_db, create_fake_dao, time_entry_factory, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id)
    inserted_time_entries = dao.create(time_entries_to_insert)

    time_entry = dao.get_by_id(time_entries_to_insert.id)

    assert isinstance(time_entry, domain.TimeEntry)
    assert time_entry.id == inserted_time_entries.id
    assert time_entry == inserted_time_entries


def test__get_by_id__returns_none__when_no_time_entry_matches_by_id(
    test_db, create_fake_dao, time_entry_factory, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id)
    dao.create(time_entries_to_insert)

    time_entry = dao.get_by_id(Faker().pyint())

    assert time_entry is None


def test_get_latest_entries__returns_a_list_of_latest_time_entries__when_an_owner_id_match(
    create_fake_dao, time_entry_factory, insert_activity, activity_factory, test_db
):
    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)
    time_entry_to_insert = time_entry_factory(
        activity_id=inserted_activity.id,
        technologies="[jira,sql]")
    inserted_time_entry = dao.create(time_entry_to_insert)

    result = dao.get_latest_entries(int(inserted_time_entry.owner_id))

    assert result == [inserted_time_entry.__dict__]


def test_get_latest_entries__returns_None__when_an_owner_id_is_not_found(
    create_fake_dao, test_db, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    insert_activity(activity_factory(), dao.db)

    result = dao.get_latest_entries(Faker().pyint())

    assert result is None
