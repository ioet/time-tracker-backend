import pytest


import time_tracker.time_entries._domain as domain
import time_tracker.time_entries._infrastructure as infrastructure
from time_tracker._infrastructure import DB


@pytest.fixture(name='create_fake_dao')
def _create_fake_dao() -> domain.TimeEntriesDao:
    db_fake = DB('sqlite:///:memory:')
    dao = infrastructure.TimeEntriesSQLDao(db_fake)
    return dao


@pytest.fixture(name='clean_database', autouse=True)
def _clean_database():
    yield
    db_fake = DB('sqlite:///:memory:')
    dao = infrastructure.TimeEntriesSQLDao(db_fake)
    query = dao.time_entry.delete()
    dao.db.get_session().execute(query)


def test__time_entry__returns_a_time_entry_dto__when_saves_correctly_with_sql_database(
    time_entry_factory, create_fake_dao, insert_activity, activity_factory
):
    dao = create_fake_dao
    inserted_activity = insert_activity(activity_factory(), dao.db)

    existent_time_entry = time_entry_factory(activity_id=inserted_activity.id, technologies="[jira,sql]")

    inserted_time_entry = dao.create(existent_time_entry)

    assert isinstance(inserted_time_entry, domain.TimeEntry)
    assert inserted_time_entry == existent_time_entry


def test__time_entry__returns_None__when_not_saves_correctly(
    time_entry_factory, create_fake_dao,
):
    dao = create_fake_dao
    existent_time_entry = time_entry_factory(activity_id=1203, technologies="[jira,sql]")

    inserted_time_entry = dao.create(existent_time_entry)

    assert inserted_time_entry is None
