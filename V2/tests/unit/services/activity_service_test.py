from time_entries._domain import ActivityService
from faker import Faker


def test__get_all__uses_the_activity_dao__to_retrieve_activities(mocker):
    expected_activities = mocker.Mock()
    activity_dao = mocker.Mock(
        get_all=mocker.Mock(return_value=expected_activities)
    )
    activity_service = ActivityService(activity_dao)

    actual_activities = activity_service.get_all()

    assert activity_dao.get_all.called
    assert expected_activities == actual_activities


def test__get_by_id__uses_the_activity_dao__to_retrieve_one_activity(mocker):
    expected_activity = mocker.Mock()
    activity_dao = mocker.Mock(
        get_by_id=mocker.Mock(return_value=expected_activity)
    )
    activity_service = ActivityService(activity_dao)

    actual_activity = activity_service.get_by_id(Faker().uuid4())

    assert activity_dao.get_by_id.called
    assert expected_activity == actual_activity
