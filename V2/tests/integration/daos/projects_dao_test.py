import pytest
import typing
from faker import Faker

from time_tracker.projects import _domain as domain
from time_tracker.projects import _infrastructure as infrastructure
from time_tracker._infrastructure import DB


@pytest.fixture(name='create_fake_dao')
def _create_fake_dao() -> domain.ProjectsDao:
    db_fake = DB()
    dao = infrastructure.ProjectsSQLDao(db_fake)
    return dao


@pytest.fixture(name='clean_database', autouse=True)
def _clean_database():
    yield
    db_fake = DB()
    dao = infrastructure.ProjectsSQLDao(db_fake)
    query = dao.project.delete()
    dao.db.get_session().execute(query)


def test__create_project__returns_a_project_dto__when_saves_correctly_with_sql_database(
    create_fake_dao, project_factory, insert_customer, customer_factory
):
    dao = create_fake_dao
    inserted_customer = insert_customer(customer_factory(), dao.db)
    project_to_insert = project_factory(customer_id=inserted_customer.id)

    inserted_project = dao.create(project_to_insert)

    expected_project = project_to_insert.__dict__
    expected_project.update({"customer": inserted_customer.__dict__})

    assert isinstance(inserted_project, domain.Project)
    assert inserted_project == project_to_insert


def test_update__returns_an_update_project__when_an_project_matching_its_id_is_found_with_sql_database(
    create_fake_dao, insert_project
):
    dao = create_fake_dao

    inserted_project = insert_project()

    expected_description = Faker().sentence()
    updated_project = dao.update(inserted_project.id, {"description": expected_description})

    assert isinstance(updated_project, domain.Project)
    assert updated_project.id == inserted_project.id
    assert updated_project.description == expected_description


def test_update__returns_none__when_no_project_matching_its_id_is_found_with_sql_database(
    create_fake_dao, project_factory
):
    dao = create_fake_dao
    project_to_insert = project_factory()

    results = dao.update(project_to_insert.id,  {"description": Faker().sentence()})

    assert results is None


def test__get_all__returns_a_list_of_project_dto_objects__when_one_or_more_projects_are_found_with_sql_database(
    create_fake_dao, insert_project
):
    dao = create_fake_dao

    inserted_projects = [
        insert_project(),
        insert_project()
    ]

    projects = dao.get_all()

    assert isinstance(projects, typing.List)
    assert projects == inserted_projects


def test_get_by_id__returns_an_project_dto__when_found_one_project_that_matches_its_id_with_sql_database(
    create_fake_dao, insert_project
):
    dao = create_fake_dao

    inserted_project = insert_project()

    project = dao.get_by_id(inserted_project.id)

    assert isinstance(project, domain.Project)
    assert project.id == inserted_project.id
    assert project == inserted_project


def test__get_by_id__returns_none__when_no_project_matches_its_id_with_sql_database(
    create_fake_dao, project_factory
):
    dao = create_fake_dao
    project_to_insert = project_factory()

    project = dao.get_by_id(project_to_insert.id)

    assert project is None


def test_get_all__returns_an_empty_list__when_doesnt_found_any_projects_with_sql_database(
    create_fake_dao
):
    projects = create_fake_dao.get_all()

    assert isinstance(projects, typing.List)
    assert projects == []


def test_delete__returns_an_project_with_inactive_status__when_an_project_matching_its_id_is_found_with_sql_database(
    create_fake_dao, insert_project
):
    dao = create_fake_dao

    inserted_project = insert_project()

    project = dao.delete(inserted_project.id)

    assert isinstance(project, domain.Project)
    assert project.id == inserted_project.id
    assert project.status == 0
    assert project.deleted is True


def test_delete__returns_none__when_no_project_matching_its_id_is_found_with_sql_database(
    create_fake_dao, project_factory
):
    dao = create_fake_dao
    project_to_insert = project_factory()

    results = dao.delete(project_to_insert.id)

    assert results is None
