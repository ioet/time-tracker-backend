from time_tracker.time_entries._application import _time_entries as time_entries

import azure.functions as func
import json


ACTIVITY_URL = "/api/time-entries/"


def test__time_entry_azure_endpoint__creates_an_time_entry__when_time_entry_has_all_attributes(
    create_temp_time_entries, time_entry_factory
):
    time_entries_json, tmp_directory = create_temp_time_entries
    time_entries._create_time_entry._JSON_PATH = tmp_directory

    time_entry_body = time_entry_factory(None).__dict__
    body = json.dumps(time_entry_body).encode("utf-8")
    req = func.HttpRequest(
        method="POST",
        body=body,
        url=ACTIVITY_URL,
    )

    response = time_entries.create_time_entry(req)
    time_entry_json_data = response.get_body()
    assert response.status_code == 201
    assert time_entry_json_data == body
