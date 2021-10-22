from time_entries._infrastructure import ActivitiesJsonDao
from time_entries._domain import Activity
from faker import Faker
import json
import pytest
import typing


@pytest.fixture(name='create_fake_activities')
def _create_fake_activities(mocker) -> typing.List[Activity]:
    def _creator(activities):
        read_data = json.dumps(activities)
        mocker.patch('builtins.open', mocker.mock_open(read_data=read_data))
        return [Activity(**activity) for activity in activities]

    return _creator


def test_get_by_id__returns_an_activity_dto__when_found_one_activity_that_matches_its_id(
    create_fake_activities,
):
    activities_json_dao = ActivitiesJsonDao(Faker().file_path())
    activities = create_fake_activities(
        [
            {
                "name": "test_name",
                "description": "test_description",
                "tenant_id": "test_tenant_id",
                "id": "test_id",
                "deleted": "test_deleted",
                "status": "test_status",
            }
        ]
    )
    activity_dto = activities.pop()

    result = activities_json_dao.get_by_id(activity_dto.id)

    assert result == activity_dto


def test__get_by_id__returns_none__when_no_activity_matches_its_id(
    create_fake_activities,
):
    activities_json_dao = ActivitiesJsonDao(Faker().file_path())
    create_fake_activities([])

    result = activities_json_dao.get_by_id(Faker().uuid4())

    assert result == None


def test__get_all__returns_a_list_of_activity_dto_objects__when_one_or_more_activities_are_found(
    create_fake_activities,
):
    activities_json_dao = ActivitiesJsonDao(Faker().file_path())
    number_of_activities = 3
    activities = create_fake_activities(
        [
            {
                "name": "test_name",
                "description": "test_description",
                "tenant_id": "test_tenant_id",
                "id": "test_id",
                "deleted": "test_deleted",
                "status": "test_status",
            }
        ]
        * number_of_activities
    )

    result = activities_json_dao.get_all()

    assert result == activities


def test_get_all__returns_an_empty_list__when_doesnt_found_any_activities(
    create_fake_activities,
):
    activities_json_dao = ActivitiesJsonDao(Faker().file_path())
    activities = create_fake_activities([])

    result = activities_json_dao.get_all()

    assert result == activities