import pytest
from faker import Faker

import time_tracker.activities._domain as activities_domain
import time_tracker.time_entries._domain as time_entries_domain
import time_tracker.customers._domain as customers_domain
import time_tracker.activities._infrastructure as activities_infrastructure
import time_tracker.customers._infrastructure as customers_infrastructure
import time_tracker.projects._domain as projects_domain
import time_tracker.projects._infrastructure as projects_infrastructure
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
        technologies=str(Faker().pylist()),
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


@pytest.fixture(name='project_factory')
def _project_factory() -> projects_domain.Project:
    def _make_project(
        id=Faker().pyint(),
        name=Faker().name(),
        description=Faker().sentence(),
        project_type_id=Faker().pyint(),
        customer_id=Faker().pyint(),
        status=Faker().pyint(),
        deleted=False,
        technologies=str(Faker().pylist()),
        customer=None
    ):
        project = projects_domain.Project(
            id=id,
            name=name,
            description=description,
            project_type_id=project_type_id,
            customer_id=customer_id,
            status=status,
            deleted=deleted,
            technologies=technologies,
            customer=customer
            )
        return project
    return _make_project


@pytest.fixture(name='insert_customer')
def _insert_customer() -> customers_domain.Customer:
    def _new_customer(customer: customers_domain.Customer, database: DB):
        dao = customers_infrastructure.CustomersSQLDao(database)
        new_customer = dao.create(customer)
        return new_customer
    return _new_customer


@pytest.fixture(name='insert_project')
def _insert_project(test_db, insert_customer, project_factory, customer_factory) -> projects_domain.Project:
    inserted_customer = insert_customer(customer_factory(), test_db)

    def _new_project():
        project_to_insert = project_factory(id=None, customer_id=inserted_customer.id, deleted=False)
        dao = projects_infrastructure.ProjectsSQLDao(test_db)
        inserted_project = dao.create(project_to_insert)
        return inserted_project
    return _new_project
