import pytest
from faker import Faker

import time_tracker.activities._domain as domain_activities
import time_tracker.activities._infrastructure as infrastructure_activities
import time_tracker.time_entries._domain as domain_time_entries
from time_tracker._infrastructure import DB


@pytest.fixture(name='activity_factory')
def _activity_factory() -> domain_activities.Activity:
    def _make_activity(
        name: str = Faker().name(), description: str = Faker().sentence(), deleted: bool = False, status: int = 1
    ):
        activity = domain_activities.Activity(
            id=None,
            name=name,
            description=description,
            deleted=deleted,
            status=status
            )
        return activity
    return _make_activity


@pytest.fixture(name='create_fake_database')
def _create_fake_database() -> DB:
    db_fake = DB('sqlite:///:memory:')
    return db_fake


@pytest.fixture(name='time_entry_factory')
def _time_entry_factory() -> domain_time_entries.TimeEntry:
    def _make_time_entry(
        id=Faker().random_int(),
        start_date=str(Faker().date_time()),
        owner_id=Faker().random_int(),
        description=Faker().sentence(),
        activity_id=Faker().random_int(),
        uri=Faker().domain_name(),
        technologies=["jira", "git"],
        end_date=str(Faker().date_time()),
        deleted=False,
        timezone_offset="300",
        project_id=Faker().random_int(),
    ):
        time_entry = domain_time_entries.TimeEntry(
            id=id,
            start_date=start_date,
            owner_id=owner_id,
            description=description,
            activity_id=activity_id,
            uri=uri,
            technologies=technologies,
            end_date=end_date,
            deleted=deleted,
            timezone_offset=timezone_offset,
            project_id=project_id,
            )
        return time_entry
    return _make_time_entry


@pytest.fixture(name='insert_activity')
def _insert_activity() -> dict:
    def _new_activity(activity: domain_activities.Activity, database: DB):
        dao = infrastructure_activities.ActivitiesSQLDao(database)
        new_activity = dao.create(activity)
        return new_activity
    return _new_activity
