from time_entries._application._activities import (
    _get_activities,
    _delete_activity,
)
import azure.functions as func
import json
import typing


def test__activity_azure_endpoint__returns_all_activities(
    create_temp_activities,
):
    activities_json, tmp_directory = create_temp_activities
    _get_activities.JSON_PATH = tmp_directory
    req = func.HttpRequest(method='GET', body=None, url='/api/activities')

    response = _get_activities.get_activities(req)
    activities_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activities_json_data == json.dumps(activities_json)


def test__activity_azure_endpoint__returns_an_activity__when_activity_matches_its_id(
    create_temp_activities,
):
    activities_json, tmp_directory = create_temp_activities
    _get_activities.JSON_PATH = tmp_directory
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/activities/',
        route_params={"id": activities_json[0]['id']},
    )

    response = _get_activities.get_activities(req)
    activitiy_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(activities_json[0])


def test__activity_azure_endpoint__returns_an_activity_with_inactive_status__when_an_activity_matching_its_id_is_found(
    create_temp_activities,
):
    activities_json, tmp_directory = create_temp_activities
    _delete_activity.JSON_PATH = tmp_directory
    req = func.HttpRequest(
        method='DELETE',
        body=None,
        url='/api/activities/',
        route_params={"id": activities_json[0]['id']},
    )

    response = _delete_activity.delete_activity(req)
    activity_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == 200
    assert activity_json_data['status'] == 'inactive'
