import pyodbc

import pytest
from flask.testing import FlaskClient
from flask_restplus._http import HTTPStatus
from pytest_mock import MockFixture

unexpected_errors_to_be_handled = [pyodbc.OperationalError]


def test_app_exists(app):
    assert app is not None


@pytest.mark.parametrize("error_type", unexpected_errors_to_be_handled)
def test_exceptions_are_handled(error_type, client: FlaskClient, mocker: MockFixture):
    from time_tracker_api.time_entries.time_entries_namespace import time_entries_dao
    mocker.patch.object(time_entries_dao,
                        "get_all",
                        side_effect=error_type)

    response = client.get('/time-entries', follow_redirects=True)

    assert HTTPStatus.INTERNAL_SERVER_ERROR != response.status_code
