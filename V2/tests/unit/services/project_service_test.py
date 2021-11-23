from faker import Faker

from time_tracker.projects._domain import ProjectService


def test__get_all__uses_the_project_dao__to_retrieve_projects(mocker):
    expected_projects = mocker.Mock()
    project_dao = mocker.Mock(
        get_all=mocker.Mock(return_value=expected_projects)
    )
    project_service = ProjectService(project_dao)

    actual_projects = project_service.get_all()

    assert project_dao.get_all.called
    assert expected_projects == actual_projects


def test__get_by_id__uses_the_project_dao__to_retrieve_one_project(mocker):
    expected_project = mocker.Mock()
    project_dao = mocker.Mock(
        get_by_id=mocker.Mock(return_value=expected_project)
    )
    project_service = ProjectService(project_dao)

    actual_project = project_service.get_by_id(Faker().pyint())

    assert project_dao.get_by_id.called
    assert expected_project == actual_project


def test__delete_project__uses_the_project_dao__to_change_project_status(
    mocker,
):
    expected_project = mocker.Mock()
    project_dao = mocker.Mock(
        delete=mocker.Mock(return_value=expected_project)
    )

    project_service = ProjectService(project_dao)
    deleted_project = project_service.delete(Faker().pyint())

    assert project_dao.delete.called
    assert expected_project == deleted_project


def test__update_project__uses_the_project_dao__to_update_one_project(
    mocker,
):
    expected_project = mocker.Mock()
    project_dao = mocker.Mock(
        update=mocker.Mock(return_value=expected_project)
    )
    project_service = ProjectService(project_dao)

    updated_project = project_service.update(
        Faker().pyint(), Faker().pydict()
    )

    assert project_dao.update.called
    assert expected_project == updated_project


def test__create_project__uses_the_project_dao__to_create_an_project(mocker, project_factory):
    expected_project = mocker.Mock()
    project_dao = mocker.Mock(
        create=mocker.Mock(return_value=expected_project)
    )
    project_service = ProjectService(project_dao)

    actual_project = project_service.create(project_factory())

    assert project_dao.create.called
    assert expected_project == actual_project
