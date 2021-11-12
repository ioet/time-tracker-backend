from time_tracker.time_entries._application import _time_entries as time_entries
from faker import Faker

import azure.functions as func
import json


ACTIVITY_URL = "/api/time-entries/"


def test__time_entry_azure_endpoint__creates_an_time_entry__when_time_entry_has_all_attributes(
    create_temp_time_entries,
):
    time_entries_json, tmp_directory = create_temp_time_entries
    time_entries._create_time_entry._JSON_PATH = tmp_directory

    time_entry_body = {
        "id": None,
        "start_date": Faker().date(),
        "owner_id": Faker().random_int(),
        "description": Faker().sentence(),
        "activity_id": Faker().random_int(),
        "uri": "http://timetracker.com",
        "technologies": ["jira", "git"],
        "end_date": Faker().date(),
        "deleted": False,
        "timezone_offset": "300",
        "project_id": Faker().random_int(),
    }
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
