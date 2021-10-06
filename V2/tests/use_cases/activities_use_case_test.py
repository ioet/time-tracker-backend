import pytest
from pytest_mock import MockFixture
from faker import Faker

from V2.source import use_cases
from V2.source.daos.activities_json_dao import ActivitiesJsonDao

fake = Faker()


def test__get_list_activities_function__uses_the_activities_service__to_retrieve_activities(mocker: MockFixture):
    expected_activities = mocker.Mock()
    use_cases.get_list_activities = mocker.Mock(return_value=expected_activities)

    actual_activities = use_cases.get_list_activities()

    assert use_cases.get_list_activities.called
    assert expected_activities == actual_activities


def test__get_activity_by_id_function__uses_the_activities_service__to_retrieve_activity(mocker: MockFixture):
    expected_activity = mocker.Mock()
    use_cases.get_activity_by_id = mocker.Mock(return_value=expected_activity)

    actual_activity = use_cases.get_activity_by_id(fake.uuid4())

    assert use_cases.get_activity_by_id.called
    assert expected_activity == actual_activity
