import pytest
from _pytest.fixtures import FixtureRequest
from flask import Flask
from flask.testing import FlaskClient

from time_tracker_api import create_app

CONFIGURATIONS = ['AzureSQLDatabaseDevelopTestConfig']


@pytest.fixture(scope='session', params=CONFIGURATIONS)
def app(request: FixtureRequest) -> Flask:
    return create_app("time_tracker_api.config.%s" % request.param)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    with app.test_client() as c:
        return c


@pytest.fixture(scope="module")
def sql_repository():
    from .resources import PersonSQLModel
    from time_tracker_api.database import seeder
    from time_tracker_api.sql_repository import db

    seeder.fresh()

    from time_tracker_api.sql_repository import SQLRepository
    yield SQLRepository(PersonSQLModel)

    db.drop_all()
    print("Models for test removed!")
