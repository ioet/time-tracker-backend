import pytest
from faker import Faker

import time_tracker.activities._domain as activities_domain
import time_tracker.time_entries._domain as time_entries_domain
import time_tracker.customers._domain as customers_domain
import time_tracker.activities._infrastructure as activities_infrastructure
from time_tracker._infrastructure import DB


@pytest.fixture(name='activity_factory')
def _activity_factory() -> activities_domain.Activity:
    def _make_activity(
        name: str = Faker().name(),
        description: str = Faker().sentence(),
        deleted: bool = False,
        status: int = 1,
    ):
        activity = activities_domain.Activity(
            id=None,
            name=name,
            description=description,
            deleted=deleted,
            status=status
            )
        return activity

    return _make_activity


@pytest.fixture(name='test_db')
def _test_db() -> DB:
    db_fake = DB()
    db_fake.get_session().execute("pragma foreign_keys=ON")
    return db_fake


@pytest.fixture(name='time_entry_factory')
def _time_entry_factory() -> time_entries_domain.TimeEntry:
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
        time_entry = time_entries_domain.TimeEntry(
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
    def _new_activity(activity: activities_domain.Activity, database: DB):
        dao = activities_infrastructure.ActivitiesSQLDao(database)
        new_activity = dao.create(activity)
        return new_activity
    return _new_activity


@pytest.fixture(name='customer_factory')
def _customer_factory() -> customers_domain.Customer:
    def _make_customer(
        name: str = Faker().name(),
        description: str = Faker().sentence(),
        deleted: bool = False,
        status: int = 1,
    ):
        customer = customers_domain.Customer(
            id=None,
            name=name,
            description=description,
            deleted=deleted,
            status=status
            )
        return customer

    return _make_customer
