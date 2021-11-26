import json
from http import HTTPStatus

from faker import Faker
import azure.functions as func

from time_tracker.projects._application import _projects as azure_projects

PROJECT_URL = '/api/projects/'


def test__project_azure_endpoint__returns_all_projects(
    insert_project
):
    inserted_projects = [
        insert_project().__dict__,
        insert_project().__dict__
    ]

    req = func.HttpRequest(method='GET', body=None, url=PROJECT_URL)
    response = azure_projects._get_projects.get_projects(req)
    projects_json_data = response.get_body().decode("utf-8")

    assert response.status_code == HTTPStatus.OK
    assert projects_json_data == json.dumps(inserted_projects)


def test__project_azure_endpoint__returns_a_project__when_project_matches_its_id(
    insert_project
):
    inserted_project = insert_project().__dict__

    req = func.HttpRequest(
        method='GET',
        body=None,
        url=PROJECT_URL,
        route_params={"id": inserted_project["id"]},
    )

    response = azure_projects._get_projects.get_projects(req)
    activitiy_json_data = response.get_body().decode("utf-8")

    assert response.status_code == HTTPStatus.OK
    assert activitiy_json_data == json.dumps(inserted_project)


def test__projects_azure_endpoint__returns_a_status_code_400__when_project_receive_invalid_id(
):
    req = func.HttpRequest(
        method="GET",
        body=None,
        url=PROJECT_URL,
        route_params={"id": "invalid id"},
    )

    response = azure_projects._get_projects.get_projects(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b"Invalid Format ID"


def test__project_azure_endpoint__returns_a_project_with_inactive_status__when_a_project_matching_its_id_is_found(
    insert_project
):
    inserted_project = insert_project().__dict__

    req = func.HttpRequest(
        method='DELETE',
        body=None,
        url=PROJECT_URL,
        route_params={"id": inserted_project["id"]},
    )

    response = azure_projects._delete_project.delete_project(req)
    project_json_data = json.loads(response.get_body().decode("utf-8"))

    assert response.status_code == HTTPStatus.OK
    assert project_json_data['status'] == 0
    assert project_json_data['deleted'] is True


def test__delete_projects_azure_endpoint__returns_a_status_code_400__when_project_receive_invalid_id(
):
    req = func.HttpRequest(
        method="DELETE",
        body=None,
        url=PROJECT_URL,
        route_params={"id": "invalid id"},
    )

    response = azure_projects._delete_project.delete_project(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b"Invalid Format ID"


def test__delete_projects_azure_endpoint__returns_a_status_code_404__when_no_found_a_project_to_delete(
):
    req = func.HttpRequest(
        method="DELETE",
        body=None,
        url=PROJECT_URL,
        route_params={"id": Faker().pyint()},
    )

    response = azure_projects._delete_project.delete_project(req)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.get_body() == b"Not found"


def test__update_project_azure_endpoint__returns_a_project__when_found_a_project_to_update(
    insert_project
):
    inserted_project = insert_project().__dict__

    project_body = {"description": Faker().sentence()}
    req = func.HttpRequest(
        method='PUT',
        body=json.dumps(project_body).encode("utf-8"),
        url=PROJECT_URL,
        route_params={"id": inserted_project["id"]},
    )

    response = azure_projects._update_project.update_project(req)
    activitiy_json_data = response.get_body().decode("utf-8")
    inserted_project.update(project_body)

    assert response.status_code == HTTPStatus.OK
    assert activitiy_json_data == json.dumps(inserted_project)


def test__update_projects_azure_endpoint__returns_a_status_code_404__when_no_found_a_project_to_update(
):
    project_body = {"description": Faker().sentence()}

    req = func.HttpRequest(
        method="PUT",
        body=json.dumps(project_body).encode("utf-8"),
        url=PROJECT_URL,
        route_params={"id": Faker().pyint()},
    )

    response = azure_projects._update_project.update_project(req)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.get_body() == b"Not found"


def test__update_projects_azure_endpoint__returns_a_status_code_400__when_receive_an_incorrect_body(
):
    project_body = Faker().pydict(5, True, str)
    req = func.HttpRequest(
        method="PUT",
        body=json.dumps(project_body).encode("utf-8"),
        url=PROJECT_URL,
        route_params={"id": Faker().pyint()},
    )

    response = azure_projects._update_project.update_project(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b"Incorrect body"


def test__update_projects_azure_endpoint__returns_a_status_code_400__when_project_receive_invalid_id(
):
    req = func.HttpRequest(
        method="PUT",
        body=None,
        url=PROJECT_URL,
        route_params={"id": "invalid id"},
    )

    response = azure_projects._update_project.update_project(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == b"Invalid Format ID"


def test__project_azure_endpoint__creates_a_project__when_project_has_all_attributes(
    test_db, project_factory, insert_customer, customer_factory
):
    inserted = insert_customer(customer_factory(), test_db)
    project_body = project_factory(inserted.id).__dict__

    req = func.HttpRequest(
         method='POST',
         body=json.dumps(project_body).encode("utf-8"),
         url=PROJECT_URL,
    )

    response = azure_projects._create_project.create_project(req)
    project_json_data = json.loads(response.get_body())
    project_body['id'] = project_json_data['id']

    assert response.status_code == HTTPStatus.CREATED
    assert project_json_data == project_body


def test__project_azure_endpoint__returns_a_status_code_400__when_project_does_not_all_attributes(
    test_db, project_factory, insert_customer, customer_factory
):
    inserted_customer = insert_customer(customer_factory(), test_db)
    project_body = project_factory(customer_id=inserted_customer.id).__dict__
    project_body.pop('name')

    req = func.HttpRequest(
         method='POST',
         body=json.dumps(project_body).encode("utf-8"),
         url=PROJECT_URL,
    )

    response = azure_projects._create_project.create_project(req)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_body() == json.dumps(['The name key is missing in the input data']).encode()


def test__project_azure_endpoint__returns_a_status_code_500__when_project_receive_incorrect_type_data(
    project_factory, insert_customer, customer_factory, test_db
):
    insert_customer(customer_factory(), test_db)
    project_body = project_factory(technologies=Faker().pylist(2, True, str)).__dict__

    req = func.HttpRequest(
        method='POST',
        body=json.dumps(project_body).encode("utf-8"),
        url=PROJECT_URL,
    )

    response = azure_projects._create_project.create_project(req)

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.get_body() == b"could not be created"
