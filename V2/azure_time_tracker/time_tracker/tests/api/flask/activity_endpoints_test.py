from time_tracker.source.entry_points.flask_api import create_app
import json
import pytest
import typing
from flask.testing import FlaskClient
from http import HTTPStatus
from faker import Faker


@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        yield client


def test_test__activity_endpoint__returns_all_activities(
    client: FlaskClient, activities_json: typing.List[dict]
):
    response = client.get("/activities/")
    json_data = json.loads(response.data)

    assert response.status_code == HTTPStatus.OK
    assert json_data == activities_json


def test__activity_endpoint__returns_an_activity__when_activity_matches_its_id(
    client: FlaskClient, activities_json: typing.List[dict]
):
    response = client.get("/activities/%s" % activities_json[0]['id'])
    json_data = json.loads(response.data)

    assert response.status_code == HTTPStatus.OK
    assert json_data == activities_json[0]


def test__activity_endpoint__returns_a_not_found_status__when_no_activity_matches_its_id(
    client: FlaskClient,
):
    response = client.get("/activities/%s" % Faker().uuid4())
    json_data = json.loads(response.data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert json_data['message'] == 'Activity not found'
