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
