import pytest
from flask import Flask
from flask.testing import FlaskClient

from time_tracker_api import create_app


@pytest.fixture(scope='session')
def app() -> Flask:
    return create_app("time_tracker_api.config.TestConfig")


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    with app.test_client() as c:
        return c


@pytest.fixture(scope="module")
def sql_repository(app: Flask):
    with app.test_client():
        from tests.commons.data_access_layer.azure.resources import PersonSQLModel
        from commons.data_access_layer.azure.sql_repository import db

        db.metadata.create_all(bind=db.engine, tables=[PersonSQLModel.__table__])
        print("Test models created!")

        from commons.data_access_layer.azure.sql_repository import SQLRepository
        yield SQLRepository(PersonSQLModel)

        db.metadata.drop_all(bind=db.engine, tables=[PersonSQLModel.__table__])
        print("Test models removed!")
