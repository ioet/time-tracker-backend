import pytest
import json
from faker import Faker

import azure.functions as func

import time_tracker.activities._application._activities as azure_activities
import time_tracker.activities._infrastructure as infrastructure
from time_tracker._infrastructure import DB
from time_tracker.activities import _domain

ACTIVITY_URL = '/api/activities/'


@pytest.fixture(name='insert_activity')
def _insert_activity() -> dict:
    def _new_activity(activity: _domain.Activity, database: DB):
        dao = infrastructure.ActivitiesSQLDao(database)
        new_activity = dao.create(activity)
        return new_activity.__dict__
    return _new_activity


def test__activity_azure_endpoint__returns_all_activities(
    create_fake_database, activity_factory, insert_activity
):
    fake_database = create_fake_database
    existent_activities = [activity_factory(), activity_factory()]
    inserted_activities = [
        insert_activity(existent_activities[0], fake_database),
        insert_activity(existent_activities[1], fake_database)
    ]

    azure_activities._get_activities.DATABASE = fake_database
    req = func.HttpRequest(method='GET', body=None, url=ACTIVITY_URL)
    response = azure_activities._get_activities.get_activities(req)
    activities_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activities_json_data == json.dumps(inserted_activities)


def test__activity_azure_endpoint__returns_an_activity__when_activity_matches_its_id(
    create_fake_database, activity_factory, insert_activity
):
    fake_database = create_fake_database
    existent_activity = activity_factory()
    inserted_activity = insert_activity(existent_activity, fake_database)

    azure_activities._get_activities.DATABASE = fake_database
    req = func.HttpRequest(
        method='GET',
        body=None,
        url=ACTIVITY_URL,
        route_params={"id": inserted_activity["id"]},
    )

    response = azure_activities._get_activities.get_activities(req)
    activitiy_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(inserted_activity)


def test__activity_azure_endpoint__returns_an_activity_with_inactive_status__when_an_activity_matching_its_id_is_found(
    create_fake_database, activity_factory, insert_activity
):
    fake_database = create_fake_database
    existent_activity = activity_factory()
    inserted_activity = insert_activity(existent_activity, fake_database)

    azure_activities._delete_activity.DATABASE = fake_database
    req = func.HttpRequest(
        method='DELETE',
        body=None,
        url=ACTIVITY_URL,
        route_params={"id": inserted_activity["id"]},
    )

    response = azure_activities._delete_activity.delete_activity(req)
    activity_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == 200
    assert activity_json_data['status'] == 0
    assert activity_json_data['deleted'] is True


def test__update_activity_azure_endpoint__returns_an_activity__when_found_an_activity_to_update(
    create_fake_database, activity_factory, insert_activity
):
    fake_database = create_fake_database
    existent_activity = activity_factory()
    inserted_activity = insert_activity(existent_activity, fake_database)

    azure_activities._update_activity.DATABASE = fake_database
    activity_body = {"description": Faker().sentence()}
    req = func.HttpRequest(
        method='PUT',
        body=json.dumps(activity_body).encode("utf-8"),
        url=ACTIVITY_URL,
        route_params={"id": inserted_activity["id"]},
    )

    response = azure_activities._update_activity.update_activity(req)
    activitiy_json_data = response.get_body().decode("utf-8")
    inserted_activity.update(activity_body)

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(inserted_activity)


def test__activity_azure_endpoint__creates_an_activity__when_activity_has_all_attributes(
     create_fake_database,
 ):
    azure_activities._create_activity.DATABASE = create_fake_database
    activity_body = {
        'id': None,
        'name': Faker().user_name(),
        'description': Faker().sentence(),
        'deleted': False,
        'status': 1
    }
    body = json.dumps(activity_body).encode("utf-8")
    req = func.HttpRequest(
         method='POST',
         body=body,
         url=ACTIVITY_URL,
    )

    response = azure_activities._create_activity.create_activity(req)
    activitiy_json_data = json.loads(response.get_body())
    activity_body['id'] = activitiy_json_data['id']

    assert response.status_code == 201
    assert activitiy_json_data == activity_body
