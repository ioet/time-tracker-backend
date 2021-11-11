import pytest

import time_tracker.activities._domain as domain 
import time_tracker.activities._infrastructure as infrastructure 
from time_tracker._infrastructure import DB

@pytest.fixture(name='activity_factory')
def _activity_factory() -> domain.Activity:
    def _make_activity(data: dict):
        activity = domain.Activity(**data)
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