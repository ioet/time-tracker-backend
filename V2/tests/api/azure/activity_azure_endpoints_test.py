from time_entries.interface import get_activities
import azure.functions as func
import json
import typing


def test__activity_azure_endpoint__returns_all_activities(
    activities_json: typing.List[dict],
):
    req = func.HttpRequest(method='GET', body=None, url='/api/activities')

    response = get_activities(req)
    activities_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activities_json_data == json.dumps(activities_json)


def test__activity_azure_endpoint__returns_an_activity__when_activity_matches_its_id(
    activities_json: typing.List[dict],
):
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/activities/',
        route_params={"id": activities_json[0]['id']},
    )

    response = get_activities(req)
    activitiy_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(activities_json[0])
