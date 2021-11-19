import pytest
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

    time_entry_to_insert = time_entry_factory(activity_id=inserted_activity.id, technologies="[jira,sql]")

    inserted_time_entry = dao.create(time_entry_to_insert)

    assert isinstance(inserted_time_entry, domain.TimeEntry)
    assert inserted_time_entry == time_entry_to_insert


def test__time_entry__returns_None__when_not_saves_correctly(
    time_entry_factory, create_fake_dao, test_db
):
    dao = create_fake_dao(test_db)
    time_entry_to_insert = time_entry_factory(activity_id=1203, technologies="[jira,sql]")

    inserted_time_entry = dao.create(time_entry_to_insert)

    assert inserted_time_entry is None


def test_delete__returns_an_time_entry_with_true_deleted__when_an_time_entry_matching_its_id_is_found(
    create_fake_dao, test_db, time_entry_factory, insert_activity, activity_factory
):
    dao = create_fake_dao(test_db)
    inserted_activity = insert_activity(activity_factory(), dao.db)
    existent_time_entry = time_entry_factory(activity_id=inserted_activity.id, technologies="[jira,sql]")
    inserted_time_entry = dao.create(existent_time_entry)

    result = dao.delete(inserted_time_entry.id)

    assert result.deleted is True


def test_delete__returns_none__when_no_time_entry_matching_its_id_is_found(
    create_fake_dao, test_db
):
    dao = create_fake_dao(test_db)

    result = dao.delete(Faker().pyint())

    assert result is None
