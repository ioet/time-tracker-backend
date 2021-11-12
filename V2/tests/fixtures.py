import pytest

import time_tracker.activities._domain as domain
import time_tracker.activities._infrastructure as infrastructure
from time_tracker._infrastructure import DB
from faker import Faker


@pytest.fixture(name='activity_factory')
def _activity_factory() -> domain.Activity:
    def _make_activity(
        name: str = Faker().name(), description: str = Faker().sentence(), deleted: bool = False, status: int = 1
    ):
        activity = domain.Activity(
            id=None,
            name=name,
            description=description,
            deleted=deleted,
            status=status
            )
        return activity
    return _make_activity


@pytest.fixture(name='create_fake_dao')
def _create_fake_dao() -> domain.ActivitiesDao:
    db_fake = DB('sqlite:///:memory:')
    dao = infrastructure.ActivitiesSQLDao(db_fake)
    return dao


@pytest.fixture(name='create_fake_database')
def _create_fake_database() -> domain.ActivitiesDao:
    db_fake = DB('sqlite:///:memory:')
    return db_fake

@pytest.fixture
def create_temp_time_entries(tmpdir_factory):
    temporary_directory = tmpdir_factory.mktemp("tmp")
    json_file = temporary_directory.join("time_entries.json")
    time_entries = [
        {
            "id": Faker().random_int(),
            "start_date": Faker().date(),
            "owner_id": Faker().random_int(),
            "description": Faker().sentence(),
            "activity_id": Faker().random_int(),
            "uri": Faker().domain_name(),
            "technologies": ["jira", "git"],
            "end_date": Faker().date(),
            "deleted": Faker().random_int(),
            "timezone_offset": "300",
            "project_id": Faker().random_int(),
        }
    ]

@pytest.fixture(name='time_entry_factory')
def _time_entry_factory() -> TimeEntry:
    def _make_time_entry(
        id=Faker().random_int(),
        start_date=Faker().date(),
        owner_id=Faker().random_int(),
        description=Faker().sentence(),
        activity_id=Faker().random_int(),
        uri=Faker().domain_name(),
        technologies=["jira", "git"],
        end_date=Faker().date(),
        deleted=False,
        timezone_offset="300",
        project_id=Faker().random_int(),
    ):
        time_entry = TimeEntry(
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
