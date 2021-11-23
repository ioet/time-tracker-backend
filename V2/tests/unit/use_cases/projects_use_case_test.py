from pytest_mock import MockFixture
from faker import Faker

from time_tracker.projects._domain import _use_cases


def test__create_project_function__uses_the_projects_service__to_create_project(
    mocker: MockFixture, project_factory
):
    expected_project = mocker.Mock()
    project_service = mocker.Mock(
        create=mocker.Mock(return_value=expected_project)
    )

    project_use_case = _use_cases.CreateProjectUseCase(project_service)
    actual_project = project_use_case.create_project(project_factory())

    assert project_service.create.called
    assert expected_project == actual_project


def test__delete_project_function__uses_the_project_service__to_delete_project_selected(
    mocker: MockFixture,
):
    expected_project = mocker.Mock()
    project_service = mocker.Mock(delete=mocker.Mock(return_value=expected_project))

    project_use_case = _use_cases.DeleteProjectUseCase(project_service)
    deleted_project = project_use_case.delete_project(Faker().pyint())

    assert project_service.delete.called
    assert expected_project == deleted_project


def test__get_list_projects_function__uses_the_project_service__to_retrieve_projects(
    mocker: MockFixture,
):
    expected_projects = mocker.Mock()
    project_service = mocker.Mock(
        get_all=mocker.Mock(return_value=expected_projects)
    )

    projects_use_case = _use_cases.GetProjectsUseCase(project_service)
    actual_projects = projects_use_case.get_projects()

    assert project_service.get_all.called
    assert expected_projects == actual_projects


def test__get_project_by_id_function__uses_the_project_service__to_retrieve_project(
    mocker: MockFixture,
):
    expected_project = mocker.Mock()
    project_service = mocker.Mock(
        get_by_id=mocker.Mock(return_value=expected_project)
    )

    project_use_case = _use_cases.GetProjectUseCase(project_service)
    actual_project = project_use_case.get_project_by_id(Faker().pyint())

    assert project_service.get_by_id.called
    assert expected_project == actual_project


def test__update_project_function__uses_the_projects_service__to_update_an_project(
    mocker: MockFixture, project_factory
):
    expected_project = mocker.Mock()
    project_service = mocker.Mock(
        update=mocker.Mock(return_value=expected_project)
    )
    project_to_update = project_factory()

    project_use_case = _use_cases.UpdateProjectUseCase(project_service)
    updated_project = project_use_case.update_project(
        Faker().pyint(), project_to_update.__dict__
    )

    assert project_service.update.called
    assert expected_project == updated_project
