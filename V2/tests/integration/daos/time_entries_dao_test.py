import pytest


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
    create_fake_database, time_entry_factory, create_fake_dao, insert_activity, activity_factory
):
    dao = create_fake_dao(create_fake_database)
    inserted_activity = insert_activity(activity_factory(), dao.db)

    time_entry_to_insert = time_entry_factory(activity_id=inserted_activity.id, technologies="[jira,sql]")

    inserted_time_entry = dao.create(time_entry_to_insert)

    assert isinstance(inserted_time_entry, domain.TimeEntry)
    assert inserted_time_entry == time_entry_to_insert


def test__time_entry__returns_None__when_not_saves_correctly(
    time_entry_factory, create_fake_dao, create_fake_database
):
    dao = create_fake_dao(create_fake_database)
    time_entry_to_insert = time_entry_factory(activity_id=1203, technologies="[jira,sql]")

    inserted_time_entry = dao.create(time_entry_to_insert)

    assert inserted_time_entry is None
