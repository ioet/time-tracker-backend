import pytest
import json
from faker import Faker
from http import HTTPStatus

import azure.functions as func

import time_tracker.time_entries._application._time_entries as azure_time_entries
from time_tracker._infrastructure import DB
from time_tracker.time_entries import _domain as domain_time_entries
from time_tracker.time_entries import _infrastructure as infrastructure_time_entries
from time_tracker.utils.enums import ResponseEnums


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
    time_entry_body = time_entry_factory(activity_id=inserted_activity.id).__dict__

    body = json.dumps(time_entry_body).encode("utf-8")
    req = func.HttpRequest(
         method='POST',
         body=body,
         url=TIME_ENTRY_URL,
    )

    response = azure_time_entries._create_time_entry.create_time_entry(req)
    time_entry_json_data = json.loads(response.get_body())
    time_entry_body['id'] = time_entry_json_data['id']

    assert response.status_code == HTTPStatus.CREATED
    assert time_entry_json_data == time_entry_body


def test__delete_time_entries_azure_endpoint__returns_an_time_entry_with_true_deleted__when_its_id_is_found(
    test_db, time_entry_factory, insert_time_entry, insert_activity, activity_factory,
):
    inserted_activity = insert_activity(activity_factory(), test_db).__dict__
    time_entry_body = time_entry_factory(activity_id=inserted_activity["id"])
    inserted_time_entry = insert_time_entry(time_entry_body, test_db)

    req = func.HttpRequest(
        method='DELETE',
        body=None,
        url=TIME_ENTRY_URL,
        route_params={"id": inserted_time_entry.id},
    )

    response = azure_time_entries._delete_time_entry.delete_time_entry(req)
    time_entry_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == HTTPStatus.OK
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

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b'Invalid Format ID'


def test__time_entry_azure_endpoint__returns_all_time_entries(
     test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity
):
    inserted_activity = insert_activity(activity_factory(), test_db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id)
    inserted_time_entries = insert_time_entry(time_entries_to_insert, test_db).__dict__

    req = func.HttpRequest(method="GET", body=None, url=TIME_ENTRY_URL)

    response = azure_time_entries.get_time_entries(req)
    time_entries_json_data = response.get_body().decode("utf-8")
    time_entry_list = json.loads(time_entries_json_data)

    assert response.status_code == HTTPStatus.OK
    assert time_entry_list.pop() == inserted_time_entries


def test__time_entry_azure_endpoint__returns_an_time_entry__when_time_entry_matches_its_id(
     test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity
):
    inserted_activity = insert_activity(activity_factory(), test_db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id)
    inserted_time_entries = insert_time_entry(time_entries_to_insert, test_db).__dict__

    req = func.HttpRequest(
        method="GET",
        body=None,
        url=TIME_ENTRY_URL,
        route_params={"id": inserted_time_entries["id"]},
    )

    response = azure_time_entries.get_time_entries(req)
    time_entry_json_data = response.get_body().decode("utf-8")

    assert response.status_code == HTTPStatus.OK
    assert time_entry_json_data == json.dumps(inserted_time_entries)


def test__get_time_entries_azure_endpoint__returns_a_status_code_400__when_time_entry_recive_invalid_id(
    test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity
):
    inserted_activity = insert_activity(activity_factory(), test_db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id)
    insert_time_entry(time_entries_to_insert, test_db).__dict__

    req = func.HttpRequest(
        method="GET",
        body=None,
        url=TIME_ENTRY_URL,
        route_params={"id": "invalid id"},
    )

    response = azure_time_entries.get_time_entries(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b'Invalid Format ID'


def test__update_time_entry_azure_endpoint__returns_an_time_entry__when_found_an_time_entry_to_update(
    test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity
):
    inserted_activity = insert_activity(activity_factory(), test_db)
    existent_time_entries = time_entry_factory(activity_id=inserted_activity.id)
    inserted_time_entries = insert_time_entry(existent_time_entries, test_db).__dict__

    time_entry_body = {"description": Faker().sentence()}

    req = func.HttpRequest(
        method='PUT',
        body=json.dumps(time_entry_body).encode("utf-8"),
        url=TIME_ENTRY_URL,
        route_params={"id": inserted_time_entries["id"]},
    )

    response = azure_time_entries._update_time_entry.update_time_entry(req)
    activitiy_json_data = response.get_body().decode("utf-8")
    inserted_time_entries.update(time_entry_body)

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(inserted_time_entries)


def test__update_time_entries_azure_endpoint__returns_a_status_code_400__when_time_entry_recive_invalid_format_id():
    time_entry_body = {"description": Faker().sentence()}

    req = func.HttpRequest(
        method="PUT",
        body=json.dumps(time_entry_body).encode("utf-8"),
        url=TIME_ENTRY_URL,
        route_params={"id": Faker().sentence()},
    )

    response = azure_time_entries._update_time_entry.update_time_entry(req)

    assert response.status_code == 400
    assert response.get_body() == b'Invalid Format ID'


def test__update_time_entries_azure_endpoint__returns_a_status_code_404__when_not_found_an_time_entry_to_update():
    time_entry_body = {"description": Faker().sentence()}

    req = func.HttpRequest(
        method="PUT",
        body=json.dumps(time_entry_body).encode("utf-8"),
        url=TIME_ENTRY_URL,
        route_params={"id": Faker().pyint()},
    )

    response = azure_time_entries._update_time_entry.update_time_entry(req)

    assert response.status_code == 404
    assert response.get_body() == b'Not found'


def test__update_time_entries_azure_endpoint__returns_a_status_code_400__when_time_entry_recive_invalid_body():

    time_entry_body = Faker().pydict(5, True, str)
    req = func.HttpRequest(
        method="PUT",
        body=json.dumps(time_entry_body).encode("utf-8"),
        url=TIME_ENTRY_URL,
        route_params={"id": Faker().pyint()},
    )

    response = azure_time_entries._update_time_entry.update_time_entry(req)

    assert response.status_code == 400
    assert response.get_body() == b'Incorrect time entry body'


def test__get_latest_entries_azure_endpoint__returns_a_list_of_latest_time_entries__when_an_owner_id_match(
    test_db, time_entry_factory, insert_time_entry, insert_activity, activity_factory,
):
    inserted_activity = insert_activity(activity_factory(), test_db).__dict__
    time_entry_body = time_entry_factory(activity_id=inserted_activity["id"], technologies="[jira,sql]")
    inserted_time_entry = insert_time_entry(time_entry_body, test_db).__dict__

    req = func.HttpRequest(
        method='GET',
        body=None,
        url=TIME_ENTRY_URL+"latest/",
        params={"owner_id": inserted_time_entry["owner_id"]},
    )

    response = azure_time_entries._get_latest_entries.get_latest_entries(req)
    time_entry_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == HTTPStatus.OK
    assert time_entry_json_data == [inserted_time_entry]


def test__get_latest_entries_azure_endpoint__returns_not_found__when_recieve_an_invalid_owner_id(
    test_db, insert_activity, activity_factory,
):
    insert_activity(activity_factory(), test_db)

    req = func.HttpRequest(
        method='GET',
        body=None,
        url=TIME_ENTRY_URL+"latest/",
        params={"owner_id": Faker().pyint()},
    )

    response = azure_time_entries._get_latest_entries.get_latest_entries(req)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.get_body().decode("utf-8") == ResponseEnums.NOT_FOUND.value
