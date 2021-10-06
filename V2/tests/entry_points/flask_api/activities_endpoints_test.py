from V2.source.entry_points.flask_api import create_app
from V2.source import use_cases
from V2.source.dtos.activity import Activity
import json
import pytest
from http import HTTPStatus
from pytest_mock import MockFixture
from flask.testing import FlaskClient
from faker import Faker
from werkzeug.exceptions import NotFound

fake = Faker()

valid_id = fake.uuid4()

fake_activity = {
    "name": fake.company(),
    "description": fake.paragraph(),
    "tenant_id": fake.uuid4(),
    "id": valid_id,
    "deleted": fake.date(),
    "status": fake.boolean(),
}
fake_activity_dto = Activity(**fake_activity)


@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        yield client


def test__activities_class__uses_the_get_activities_use_case__to_retrieve_activities(client: FlaskClient,
                                                                                     mocker: MockFixture):
    use_cases.get_list_activities = mocker.Mock(return_value=[])

    response = client.get("/activities/")
    json_data = json.loads(response.data)

    assert response.status_code == HTTPStatus.OK
    assert [] == json_data


def test__activity_class__returns_an_activity__when_activity_matches_its_id(client: FlaskClient, mocker: MockFixture):
    use_cases.get_activity_by_id = mocker.Mock(return_value=fake_activity_dto)

    response = client.get("/activities/%s" % valid_id)

    assert response.status_code == HTTPStatus.OK
    assert fake_activity == json.loads(response.data)


def test__activity_class__returns_an_activity__when_no_activity_matches_its_id(client: FlaskClient,
                                                                               mocker: MockFixture):
    invalid_id = fake.uuid4()
    use_cases.get_activity_by_id = mocker.Mock(side_effect=NotFound)

    response = client.get("/activities/%s" % invalid_id)

    assert response.status_code == HTTPStatus.NOT_FOUND
