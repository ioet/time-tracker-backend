from V2.source.services.activity_service import ActivityService
from V2.source.daos.activities_json_dao import ActivitiesJsonDao
from V2.source.dtos.activity import Activity
import typing


class GetActivitiesUseCase:
    def get_activities(self) -> typing.List[Activity]:
        activity_json = ActivitiesJsonDao('./V2/source/activities_data.json')
        activities = ActivityService(activity_json)
        return activities.get_all()
