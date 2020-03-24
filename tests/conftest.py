import pytest
from _pytest.fixtures import FixtureRequest
from flask import Flask
from flask.testing import FlaskClient

from time_tracker_api import create_app


@pytest.fixture(scope='session')
def app(request: FixtureRequest) -> Flask:
    return create_app("time_tracker_api.config.TestConfig")


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    with app.test_client() as c:
        return c


@pytest.fixture(scope="module")
def sql_repository():
    from .resources import PersonSQLModel
    from time_tracker_api.sql_repository import db

    db.metadata.create_all(bind=db.engine, tables=[PersonSQLModel.__table__])
    print("Test models created!")

    from time_tracker_api.sql_repository import SQLRepository
    yield SQLRepository(PersonSQLModel)

    db.metadata.drop_all(bind=db.engine, tables=[PersonSQLModel.__table__])
    print("Test models removed!")
