
import pytest

from time_tracker_api import create_app

@pytest.fixture(scope='session')
def app():
    """An instance of the app for tests"""
    return create_app()

@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as c:
        return c