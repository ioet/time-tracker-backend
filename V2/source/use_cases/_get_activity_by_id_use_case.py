from V2.source.services.activity_service import ActivityService
from V2.source.daos.activities_json_dao import ActivitiesJsonDao
from V2.source.dtos.activity import Activity


class GetActivityUseCase:
    def get_activity_by_id(self, id: str) -> Activity:
        activity_json = ActivitiesJsonDao('./V2/source/activities_data.json')
        activity = ActivityService(activity_json)
        return activity.get_by_id(id)
