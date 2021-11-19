import pytest
import json

import azure.functions as func

import time_tracker.time_entries._application._time_entries as azure_time_entries
from time_tracker._infrastructure import DB
from time_tracker.time_entries import _domain as domain_time_entries
from time_tracker.time_entries import _infrastructure as infrastructure_time_entries


TIME_ENTRY_URL = "/api/time-entries/"


@pytest.fixture(name='insert_time_entry')
def _insert_time_entry() -> domain_time_entries.TimeEntry:
    def _new_time_entry(time_entry: domain_time_entries.TimeEntry, database: DB):
        dao = infrastructure_time_entries.TimeEntriesSQLDao(database)
        new_time_entry = dao.create(time_entry)
        return new_time_entry
    return _new_time_entry


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


def test__delete_time_entries_azure_endpoint__returns_an_time_entry_with_true_deleted__when_its_id_is_found(
    test_db, time_entry_factory, insert_time_entry, insert_activity, activity_factory,
):
    inserted_activity = insert_activity(activity_factory(), test_db).__dict__
    time_entry_body = time_entry_factory(activity_id=inserted_activity["id"], technologies="[jira,sql]")
    inserted_time_entry = insert_time_entry(time_entry_body, test_db)

    req = func.HttpRequest(
        method='DELETE',
        body=None,
        url=TIME_ENTRY_URL,
        route_params={"id": inserted_time_entry.id},
    )

    response = azure_time_entries._delete_time_entry.delete_time_entry(req)
    time_entry_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == 200
    assert time_entry_json_data['deleted'] is True


def test__delete_time_entries_azure_endpoint__returns_a_status_code_400__when_time_entry_recive_invalid_id(
):
    req = func.HttpRequest(
        method="DELETE",
        body=None,
        url=TIME_ENTRY_URL,
        route_params={"id": "invalid id"},
    )

    response = azure_time_entries._delete_time_entry.delete_time_entry(req)

    assert response.status_code == 400
    assert response.get_body() == b'Invalid Format ID'
