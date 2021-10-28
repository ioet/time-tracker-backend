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


def test__delete_activity__uses_the_activity_dao__to_change_activity_status(
    mocker,
):
    expected_activity = mocker.Mock()
    activity_dao = mocker.Mock(
        delete=mocker.Mock(return_value=expected_activity)
    )

    activity_service = ActivityService(activity_dao)
    deleted_activity = activity_service.delete(Faker().uuid4())

    assert activity_dao.delete.called
    assert expected_activity == deleted_activity


def test__update_activity__uses_the_activity_dao__to_update_one_activity(
    mocker,
):
    expected_activity = mocker.Mock()
    activity_dao = mocker.Mock(
        update=mocker.Mock(return_value=expected_activity)
    )
    activity_service = ActivityService(activity_dao)

    updated_activity = activity_service.update(
        Faker().uuid4(), Faker().pydict()
    )

    assert activity_dao.update.called
    assert expected_activity == updated_activity

def test__create_activity__uses_the_activity_dao__to_create_an_activity(mocker):
    expected_activity = mocker.Mock()
    activity_dao = mocker.Mock(
        create_activity=mocker.Mock(return_value=expected_activity)
    )
    activity_service = ActivityService(activity_dao)

    actual_activity = activity_service.create_activity(Faker().pydict())

    assert activity_dao.create_activity.called
    assert expected_activity == actual_activity
