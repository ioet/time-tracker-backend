import json

import azure.functions as func

import time_tracker.time_entries._application._time_entries as azure_time_entries

TIME_ENTRY_URL = "/api/time-entries/"


def test__time_entry_azure_endpoint__creates_an_time_entry__when_time_entry_has_all_attributes(
    create_fake_database, time_entry_factory, activity_factory, insert_activity
):
    db = create_fake_database
    inserted_activity = insert_activity(activity_factory(), db)
    time_entry_body = time_entry_factory(activity_id=inserted_activity.id, technologies="[jira,sql]").__dict__

    azure_time_entries._create_time_entry._DATABASE = db
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
