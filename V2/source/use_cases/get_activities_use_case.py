from V2.source.services.activity_service import ActivityService
from V2.source.daos.activities_json_dao import ActivitiesJsonDao

def get_list_activities():
    activity_json_dao = ActivitiesJsonDao('./V2/source/activities_data.json')
    activity_service = ActivityService(activity_json_dao)
    activities_dto = activity_service.get_all()
    activities = [activity_dto.__dict__ for activity_dto in activities_dto]

    return activities