from time_tracker.source.entry_points.flask_api import create_app
import json
import pytest
import typing
from flask.testing import FlaskClient
from http import HTTPStatus
from faker import Faker
import shutil


@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        yield client


@pytest.fixture
def activities_json(tmpdir_factory):
    temporary_directory = tmpdir_factory.mktemp("tmp")
    json_file = temporary_directory.join("activities.json")
    activities = [
        {
            'id': 'c61a4a49-3364-49a3-a7f7-0c5f2d15072b',
            'name': 'Development',
            'description': 'Development',
            'deleted': 'b4327ba6-9f96-49ee-a9ac-3c1edf525172',
            'status': None,
            'tenant_id': 'cc925a5d-9644-4a4f-8d99-0bee49aadd05',
        },
        {
            'id': '94ec92e2-a500-4700-a9f6-e41eb7b5507c',
            'name': 'Management',
            'description': None,
            'deleted': '7cf6efe5-a221-4fe4-b94f-8945127a489a',
            'status': None,
            'tenant_id': 'cc925a5d-9644-4a4f-8d99-0bee49aadd05',
        },
        {
            'id': 'd45c770a-b1a0-4bd8-a713-22c01a23e41b',
            'name': 'Operations',
            'description': 'Operation activities performed.',
            'deleted': '7cf6efe5-a221-4fe4-b94f-8945127a489a',
            'status': 'active',
            'tenant_id': 'cc925a5d-9644-4a4f-8d99-0bee49aadd05',
        },
    ]

    with open(json_file, 'w') as outfile:
        json.dump(activities, outfile)

    with open(json_file) as outfile:
        activities_json = json.load(outfile)

    yield activities_json
    shutil.rmtree(temporary_directory)


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
