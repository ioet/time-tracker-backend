import pytest
from flask import Flask
from flask.testing import FlaskClient

from time_tracker_api import create_app


@pytest.fixture(scope='session')
def app() -> Flask:
    """An instance of the app for tests"""
    return create_app()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for the app."""
    with app.test_client() as c:
        return c
