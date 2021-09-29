from V2.source.daos.activities_json_dao import ActivitiesJsonDao
from V2.source.dtos.activity import ActivityDto
from http import HTTPStatus
import json


def test__get_by_id__returns_an_activity_dto__when_find_activity_that_matches_its_id(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activities = [
        {
            "name": "test_name",
            "description": "test_description",
            "tenant_id": "test_tenant_id",
            "id": "test_id",
            "deleted": "test_deleted",
            "status": "test_status",
        }
    ]
    activity_dto = ActivityDto(**activities[0])

    activities_dao_mock = mocker.patch.object(
        activities_json_dao, '_ActivitiesJsonDao__get_activities_from_file'
    )
    activities_dao_mock.return_value = activities
    result = activities_json_dao.get_by_id(activity_dto.id)

    assert result == activity_dto


def test__get_by_id__return_httpstatus_not_found__when_no_activity_matches_its_id(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activity = []

    activities_dao_mock = mocker.patch.object(
        activities_json_dao, '_ActivitiesJsonDao__get_activities_from_file'
    )
    activities_dao_mock.return_value = activity
    result = activities_json_dao.get_by_id('non-important-id')

    assert result == HTTPStatus.NOT_FOUND


def test_get_all__return_list_of_activity_dto__when_find_one_or_more_activities(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activity = {
        "name": "test_name",
        "description": "test_description",
        "tenant_id": "test_tenant_id",
        "id": "test_id",
        "deleted": "test_deleted",
        "status": "test_status",
    }
    number_of_activities = 3
    activity_dto = ActivityDto(**activity)
    list_activities_dto = [activity_dto] * number_of_activities
    activities = [activity] * number_of_activities

    activities_dao_mock = mocker.patch.object(
        activities_json_dao, '_ActivitiesJsonDao__get_activities_from_file'
    )
    activities_dao_mock.return_value = activities
    result = activities_json_dao.get_all()

    assert result == list_activities_dto


def test_get_all__return_empty_list__when_doesnt_found_any_activities(mocker):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activities = []

    activities_dao_mock = mocker.patch.object(
        activities_json_dao, '_ActivitiesJsonDao__get_activities_from_file'
    )
    activities_dao_mock.return_value = activities
    result = activities_json_dao.get_all()

    assert result == activities


def test__get_activities_from_file__returns_a_list_of_activities__when_find_activities_on_a_json_file(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activities = [
        {
            "name": "test_name",
            "description": "test_description",
            "tenant_id": "test_tenant_id",
            "id": "test_id",
            "deleted": "test_deleted",
            "status": "test_status",
        }
    ]
    read_data = json.dumps(activities)

    mocker.patch('builtins.open', mocker.mock_open(read_data=read_data))
    result = activities_json_dao._ActivitiesJsonDao__get_activities_from_file()

    assert result == activities


def test__get_activities_from_file__returns_an_empty_list__when_doesnt_find_any_file(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')

    result = activities_json_dao._ActivitiesJsonDao__get_activities_from_file()

    assert result == []


def test__create_activity_dto__returns_an_activity_dto__when_input_is_an_activity_dict(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activity = {
        "name": "test_name",
        "description": "test_description",
        "tenant_id": "test_tenant_id",
        "id": "test_id",
        "deleted": "test_deleted",
        "status": "test_status",
    }
    activity_dto = ActivityDto(**activity)

    result = activities_json_dao._ActivitiesJsonDao__create_activity_dto(
        activity
    )

    assert result == activity_dto
