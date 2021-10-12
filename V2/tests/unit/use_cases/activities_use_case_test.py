from V2.source import use_cases
from pytest_mock import MockFixture
from faker import Faker

fake = Faker()


def test__get_list_activities_function__uses_the_activities_service__to_retrieve_activities(
    mocker: MockFixture,
):
    expected_activities = mocker.Mock()
    mocker.patch.object(
        use_cases.GetActivitiesUseCase,
        'get_activities',
        return_value=expected_activities,
    )

    activities_use_case = use_cases.GetActivitiesUseCase()
    actual_activities = activities_use_case.get_activities()

    assert activities_use_case.get_activities.called
    assert expected_activities == actual_activities


def test__get_activity_by_id_function__uses_the_activities_service__to_retrieve_activity(
    mocker: MockFixture,
):
    expected_activity = mocker.Mock()
    mocker.patch.object(
        use_cases.GetActivityUseCase,
        'get_activity_by_id',
        return_value=expected_activity,
    )

    activity_use_case = use_cases.GetActivityUseCase()
    actual_activity = activity_use_case.get_activity_by_id(fake.uuid4())

    assert activity_use_case.get_activity_by_id.called
    assert expected_activity == actual_activity
