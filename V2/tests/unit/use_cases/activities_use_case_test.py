from faker import Faker
from pytest_mock import MockFixture

from time_tracker.activities._domain import _use_cases

fake = Faker()


def test__get_list_activities_function__uses_the_activity_service__to_retrieve_activities(
    mocker: MockFixture,
):
    expected_activities = mocker.Mock()
    activity_service = mocker.Mock(
        get_all=mocker.Mock(return_value=expected_activities)
    )

    activities_use_case = _use_cases.GetActivitiesUseCase(activity_service)
    actual_activities = activities_use_case.get_activities()

    assert activity_service.get_all.called
    assert expected_activities == actual_activities


def test__get_activity_by_id_function__uses_the_activity_service__to_retrieve_activity(
    mocker: MockFixture,
):
    expected_activity = mocker.Mock()
    activity_service = mocker.Mock(
        get_by_id=mocker.Mock(return_value=expected_activity)
    )

    activity_use_case = _use_cases.GetActivityUseCase(activity_service)
    actual_activity = activity_use_case.get_activity_by_id(fake.uuid4())

    assert activity_service.get_by_id.called
    assert expected_activity == actual_activity


def test__create_activity_function__uses_the_activities_service__to_create_activity(
     mocker: MockFixture, activity_factory
 ):
    expected_activity = mocker.Mock()
    activity_service = mocker.Mock(
         create=mocker.Mock(return_value=expected_activity)
    )

    activity_use_case = _use_cases.CreateActivityUseCase(activity_service)
    actual_activity = activity_use_case.create_activity(activity_factory())

    assert activity_service.create.called
    assert expected_activity == actual_activity


def test__delete_activity_function__uses_the_activity_service__to_change_activity_status(
    mocker: MockFixture,
):
    expected_activity = mocker.Mock()
    activity_service = mocker.Mock(
        delete=mocker.Mock(return_value=expected_activity)
    )

    activity_use_case = _use_cases.DeleteActivityUseCase(activity_service)
    deleted_activity = activity_use_case.delete_activity(fake.uuid4())

    assert activity_service.delete.called
    assert expected_activity == deleted_activity


def test__update_activity_function__uses_the_activities_service__to_update_an_activity(
    mocker: MockFixture, activity_factory
):
    expected_activity = mocker.Mock()
    activity_service = mocker.Mock(
        update=mocker.Mock(return_value=expected_activity)
    )
    new_activity = activity_factory()

    activity_use_case = _use_cases.UpdateActivityUseCase(activity_service)
    updated_activity = activity_use_case.update_activity(
        fake.uuid4(), new_activity.name, new_activity.description, new_activity.status, new_activity.deleted
    )

    assert activity_service.update.called
    assert expected_activity == updated_activity
