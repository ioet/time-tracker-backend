from activities import main
import azure.functions as func
import json
import pytest
import typing
import shutil


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


def test__activity_azure_endpoint__returns_all_activities(
    activities_json: typing.List[dict],
):
    req = func.HttpRequest(method='GET', body=None, url='/api/activities')

    response = main(req)
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

    response = main(req)
    activitiy_json_data = response.get_body().decode("utf-8")

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(activities_json[0])
