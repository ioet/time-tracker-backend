from V2.source.services.activity_service import ActivityService
from V2.source.daos.activities_json_dao import ActivitiesJsonDao

def get_list_activities():
    activity_json_dao = ActivitiesJsonDao('./V2/source/activities_data.json')
    activity_service = ActivityService(activity_json_dao)
    list_activities_dto = activity_service.get_all()
    #print(list_activities_dto)

    list_activities_json = []

    for activity_dto in list_activities_dto:
        activity_json = {
            'id': activity_dto.id,
            'name': activity_dto.name,
            'description': activity_dto.description,
            'deleted': activity_dto.deleted,
            'status': activity_dto.status,
            'tenant_id': activity_dto.tenant_id,

        }
        list_activities_json.append(activity_json)

    #print(list_activities_json)

    return list_activities_json