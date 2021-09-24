from V2.source.services.activity_service import ActivityService
from V2.source.daos.activities_json_dao import ActivitiesJsonDao
from V2.source.dtos.activity import ActivityDto
from http import HTTPStatus


def test__get_by_id__return_activity_dto__when_find_activity_that_matches_its_id_on_activities_json_dao(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activity_service = ActivityService(activities_json_dao)
    activity = {
        "name": "test_name",
        "description": "test_description",
        "tenant_id": "test_tenant_id",
        "id": "test_id",
        "deleted": "test_deleted",
        "status": "test_status",
    }
    activity_dto = ActivityDto(**activity)

    activities_dao_mock = mocker.patch.object(ActivitiesJsonDao, 'get_by_id')
    activities_dao_mock.return_value = activity_dto
    result = activity_service.get_by_id(activity.get('id'))

    assert result == activity_dto


def test__get_by_id__return_httpstatus_not_found__when_no_activity_matches_its_id_on_activities_json_dao(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activity_service = ActivityService(activities_json_dao)

    activities_dao_mock = mocker.patch.object(ActivitiesJsonDao, 'get_by_id')
    activities_dao_mock.return_value = HTTPStatus.NOT_FOUND

    result = activity_service.get_by_id('non-important-id')

    assert result == HTTPStatus.NOT_FOUND


def test__get_all__return_list_of_activity_dto__when_find_one_or_more_activities_on_activities_json_dao(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activity_service = ActivityService(activities_json_dao)
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

    activities_dao_mock = mocker.patch.object(ActivitiesJsonDao, 'get_all')
    activities_dao_mock.return_value = list_activities_dto
    result = activity_service.get_all()

    assert result == list_activities_dto


def test__get_all__return_empty_list__when_doesnt_found_any_activities_on_activities_json_dao(
    mocker,
):
    activities_json_dao = ActivitiesJsonDao('non-important-path')
    activity_service = ActivityService(activities_json_dao)
    activities = []

    activities_dao_mock = mocker.patch.object(ActivitiesJsonDao, 'get_all')
    activities_dao_mock.return_value = activities
    result = activity_service.get_all()

    assert result == activities
