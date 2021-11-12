import json

import azure.functions as func

import time_tracker.time_entries._application._time_entries as azure_time_entries

TIME_ENTRY_URL = "/api/time-entries/"


def test__time_entry_azure_endpoint__creates_an_time_entry__when_time_entry_has_all_attributes(
    test_db, time_entry_factory, activity_factory, insert_activity
):
    inserted_activity = insert_activity(activity_factory(), test_db)
    time_entry_body = time_entry_factory(activity_id=inserted_activity.id, technologies="[jira,sql]").__dict__

    body = json.dumps(time_entry_body).encode("utf-8")
    req = func.HttpRequest(
         method='POST',
         body=body,
         url=TIME_ENTRY_URL,
    )

    response = azure_time_entries._create_time_entry.create_time_entry(req)
    time_entry_json_data = json.loads(response.get_body())
    time_entry_body['id'] = time_entry_json_data['id']

    assert response.status_code == 201
    assert time_entry_json_data == time_entry_body


def test__time_entry_azure_endpoint__returns_an_time_entry_with_true_deleted__when_an_time_entry_matching_its_id_is_found(
    create_temp_time_entries,
):
    time_entries_json, tmp_directory = create_temp_time_entries
    time_entries.delete_time_entry.JSON_PATH = tmp_directory
    req = func.HttpRequest(
        method="DELETE",
        body=None,
        url=TIME_ENTRY_URL,
        route_params={"id": time_entries_json[0]["id"]},
    )

    response = time_entries.delete_time_entry(req)
    time_entry_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == 200
    assert time_entry_json_data["deleted"] is True


def test__delete_time_entries_azure_endpoint__returns_a_status_code_400__when_time_entry_recive_invalid_id(
    create_temp_time_entries,
):
    tmp_directory = create_temp_time_entries
    time_entries.delete_time_entry.JSON_PATH = tmp_directory
    req = func.HttpRequest(
        method="DELETE",
        body=None,
        url=TIME_ENTRY_URL,
        route_params={"id": "invalid id"},
    )

    response = time_entries.delete_time_entry(req)

    assert response.status_code == 400
    assert response.get_body() == b'Invalid Format ID'