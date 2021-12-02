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
TIME_ENTRY_SUMMARY_URL = "/api/time-entries/summary/"


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
    test_db, time_entry_factory, insert_time_entry, insert_activity, activity_factory, insert_project
):
    inserted_project = insert_project()
    inserted_activity = insert_activity(activity_factory(), test_db).__dict__
    time_entry_body = time_entry_factory(activity_id=inserted_activity["id"], project_id=inserted_project.id)
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
     test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity, insert_project
):
    inserted_project = insert_project()
    inserted_activity = insert_activity(activity_factory(), test_db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id, project_id=inserted_project.id)
    inserted_time_entries = insert_time_entry(time_entries_to_insert, test_db).__dict__

    req = func.HttpRequest(method="GET", body=None, url=TIME_ENTRY_URL)

    response = azure_time_entries.get_time_entries(req)
    time_entries_json_data = response.get_body().decode("utf-8")
    time_entry_list = json.loads(time_entries_json_data)

    assert response.status_code == HTTPStatus.OK
    assert time_entry_list.pop() == inserted_time_entries


def test__time_entry_azure_endpoint__returns_an_time_entry__when_time_entry_matches_its_id(
     test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity, insert_project
):
    inserted_project = insert_project()
    inserted_activity = insert_activity(activity_factory(), test_db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id, project_id=inserted_project.id)
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
    test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity, insert_project
):
    inserted_project = insert_project()
    inserted_activity = insert_activity(activity_factory(), test_db)
    time_entries_to_insert = time_entry_factory(activity_id=inserted_activity.id, project_id=inserted_project.id)
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


def test__get_latest_entries_azure_endpoint__returns_a_list_of_latest_time_entries__when_an_owner_id_match(
    test_db, time_entry_factory, insert_time_entry, insert_activity, activity_factory, insert_project
):
    inserted_project = insert_project()
    inserted_activity = insert_activity(activity_factory(), test_db).__dict__
    time_entry_body = time_entry_factory(activity_id=inserted_activity["id"], project_id=inserted_project.id)
    inserted_time_entry = insert_time_entry(time_entry_body, test_db).__dict__

    req = func.HttpRequest(
        method='GET',
        body=None,
        url=TIME_ENTRY_URL+"latest/",
        params={"owner_id": inserted_time_entry["owner_id"]},
    )

    response = azure_time_entries._get_latest_entries.get_latest_entries(req)
    time_entry_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == 200
    assert time_entry_json_data == [inserted_time_entry]


def test__get_latest_entries_azure_endpoint__returns_no_time_entries_found__when_recieve_an_invalid_owner_id(
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

    assert response.status_code == 404
    assert response.get_body() == b'Not found'


def test__update_time_entry_azure_endpoint__returns_an_time_entry__when_found_an_time_entry_to_update(
    test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity, insert_project
):
    inserted_project = insert_project()
    inserted_activity = insert_activity(activity_factory(), test_db).__dict__
    time_entry_body = time_entry_factory(activity_id=inserted_activity["id"], project_id=inserted_project.id)
    inserted_time_entry = insert_time_entry(time_entry_body, test_db).__dict__

    time_entry_body = {"description": Faker().sentence()}

    req = func.HttpRequest(
        method='PUT',
        body=json.dumps(time_entry_body).encode("utf-8"),
        url=TIME_ENTRY_URL,
        route_params={"id": inserted_time_entry["id"]},
    )

    response = azure_time_entries._update_time_entry.update_time_entry(req)
    activitiy_json_data = response.get_body().decode("utf-8")
    inserted_time_entry.update(time_entry_body)

    assert response.status_code == 200
    assert activitiy_json_data == json.dumps(inserted_time_entry)


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


def test__time_entry_azure_endpoint__returns_the_summary(
    test_db, time_entry_factory, insert_time_entry, activity_factory, insert_activity, insert_project
):
    inserted_project = insert_project()
    inserted_activity = insert_activity(activity_factory(), test_db)
    existent_time_entries = time_entry_factory(activity_id=inserted_activity.id,
                                               owner_id=69,
                                               start_date='11/10/2021',
                                               end_date='11/11/2021',
                                               project_id=inserted_project.id)
    inserted_time_entries = insert_time_entry(existent_time_entries, test_db).__dict__

    req = func.HttpRequest(
        method='GET',
        body=None,
        url=TIME_ENTRY_SUMMARY_URL,
        params={'owner_id': inserted_time_entries['owner_id'],
                'start_date': '11/10/2021',
                'end_date': '11/11/2021'},
    )

    response = azure_time_entries.get_time_entries_summary(req)

    time_entries_obtained = response.get_body().decode("utf-8")
    assert response.status_code == HTTPStatus.OK
    assert json.loads(time_entries_obtained) == [inserted_time_entries]


def test__time_entry_summary_azure_endpoint__returns_not_found_with_invalid_owner_id(
    test_db, insert_activity, activity_factory
):

    insert_activity(activity_factory(), test_db)

    request_params = {
        "method": 'GET',
        "body": None,
        "url": TIME_ENTRY_SUMMARY_URL,
        "params": {"owner_id": 96},
    }
    req_owner_id = func.HttpRequest(**request_params)

    response_owner_id = azure_time_entries._get_time_entries_summary.get_time_entries_summary(req_owner_id)

    assert response_owner_id.status_code == HTTPStatus.NOT_FOUND
    assert response_owner_id.get_body().decode() == ResponseEnums.NOT_FOUND.value

    request_params["params"] = {"owner_id": 69, "start_date": "", "end_date": "11/11/2021"}
    req_start_date = func.HttpRequest(**request_params)

    response_start_date = azure_time_entries._get_time_entries_summary.get_time_entries_summary(req_start_date)

    assert response_start_date.status_code == HTTPStatus.NOT_FOUND
    assert response_start_date.get_body().decode() == ResponseEnums.NOT_FOUND.value


def test__time_entry_summary_azure_endpoint__returns_invalid_date_format_with_invalid_date_format(
    test_db, insert_activity, activity_factory
):

    insert_activity(activity_factory(), test_db)

    wrong_date_format = "30/11/2021"
    right_date_format = "11/30/2021"

    request_params = {
        "method": 'GET',
        "body": None,
        "url": TIME_ENTRY_SUMMARY_URL,
        "params": {"owner_id": 1, "start_date": wrong_date_format, "end_date": right_date_format},
    }

    req_owner_id = func.HttpRequest(**request_params)
    response_owner_id = azure_time_entries._get_time_entries_summary.get_time_entries_summary(req_owner_id)

    assert response_owner_id.status_code == HTTPStatus.NOT_FOUND
    assert response_owner_id.get_body().decode() == ResponseEnums.INVALID_DATE_FORMAT.value

    request_params["params"] = {"owner_id": 1, "start_date": right_date_format, "end_date": wrong_date_format}
    req_start_date = func.HttpRequest(**request_params)

    response_start_date = azure_time_entries._get_time_entries_summary.get_time_entries_summary(req_start_date)

    assert response_start_date.status_code == HTTPStatus.NOT_FOUND
    assert response_start_date.get_body().decode() == ResponseEnums.INVALID_DATE_FORMAT.value
