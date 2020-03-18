import pytest
from _pytest.fixtures import FixtureRequest
from flask import Flask
from flask.testing import FlaskClient

from time_tracker_api import create_app

CONFIGURATIONS = ['AzureSQLDatabaseDevelopTestConfig']


@pytest.fixture(scope='session', params=CONFIGURATIONS)
def app(request: FixtureRequest) -> Flask:
    """An instance of the app for tests"""
    return create_app("time_tracker_api.config.%s" % request.param)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for the app."""
    with app.test_client() as c:
        return c


@pytest.fixture()
def repository(app: Flask):
    with app.app_context():
        from .resources import TestModel
        from time_tracker_api.sql_repository import db

        db.create_all()
        print("Models for test created!")

        from time_tracker_api.sql_repository import SQLRepository
        return SQLRepository(TestModel)
