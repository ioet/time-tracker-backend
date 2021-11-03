from time_entries._application import _activities as activities
from faker import Faker

import azure.functions as func
import json
import typing


ACTIVITY_URL = '/api/activities/'


def test__activity_azure_endpoint__returns_all_activities(
    create_temp_activities,
):
    activities_json, tmp_directory = create_temp_activities
    activities._get_activities.JSON_PATH = tmp_directory
    req = func.HttpRequest(method='GET', body=None, url=ACTIVITY_URL)

    response = activities.get_activities(req)
    activities_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activities_json_data == json.dumps(activities_json)


def test__activity_azure_endpoint__returns_an_activity__when_activity_matches_its_id(
    create_temp_activities,
):
    activities_json, tmp_directory = create_temp_activities
    activities._get_activities.JSON_PATH = tmp_directory
    req = func.HttpRequest(
        method='GET',
        body=None,
        url=ACTIVITY_URL,
        route_params={"id": activities_json[0]['id']},
    )

    response = activities.get_activities(req)
    activitiy_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(activities_json[0])


def test__activity_azure_endpoint__returns_an_activity_with_inactive_status__when_an_activity_matching_its_id_is_found(
    create_temp_activities,
):
    activities_json, tmp_directory = create_temp_activities
    activities._delete_activity.JSON_PATH = tmp_directory
    req = func.HttpRequest(
        method='DELETE',
        body=None,
        url=ACTIVITY_URL,
        route_params={"id": activities_json[0]['id']},
    )

    response = activities.delete_activity(req)
    activity_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == 200
    assert activity_json_data['status'] == 'inactive'


def test__update_activity_azure_endpoint__returns_an_activity__when_found_an_activity_to_update(
    create_temp_activities,
):
    activities_json, tmp_directory = create_temp_activities
    activities._update_activity.JSON_PATH = tmp_directory
    activity_data = {"description": Faker().sentence()}
    req = func.HttpRequest(
        method='PUT',
        body=json.dumps(activity_data).encode("utf-8"),
        url=ACTIVITY_URL,
        route_params={"id": activities_json[0]['id']},
    )

    response = activities.update_activity(req)
    activitiy_json_data = response.get_body().decode("utf-8")
    new_activity = {**activities_json[0], **activity_data}

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(new_activity)

def test__activity_azure_endpoint__creates_an_activity__when_activity_has_all_attributes(
     create_temp_activities,
 ):
     activities_json, tmp_directory = create_temp_activities
     activities._create_activity._JSON_PATH = tmp_directory

     activity_body = {'id': None, 'name': Faker().user_name(), 'description': Faker().sentence(),'deleted': Faker().uuid4() ,'status': 'active', 'tenant_id': Faker().uuid4()}
     body = json.dumps(activity_body).encode("utf-8")
     req = func.HttpRequest(
         method='POST',
         body= body,
         url=ACTIVITY_URL,
     )

     response = activities.create_activity(req)
     activitiy_json_data = response.get_body()
     assert response.status_code == 201
     assert activitiy_json_data ==  body