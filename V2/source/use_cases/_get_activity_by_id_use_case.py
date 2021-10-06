from V2.source.services.activity_service import ActivityService
from V2.source.daos.activities_json_dao import ActivitiesJsonDao
from V2.source.dtos.activity import Activity

def get_activity_by_id(id: str) -> Activity:
    activity_json_dao = ActivitiesJsonDao('./V2/source/activities_data.json')
    activity_service = ActivityService(activity_json_dao)
    activity_dto = activity_service.get_by_id(id)

    return activity_dto