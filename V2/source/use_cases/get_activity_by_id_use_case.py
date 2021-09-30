from V2.source.services.activity_service import ActivityService
from V2.source.daos.activities_json_dao import ActivitiesJsonDao

def get_activity_by_id(id: str):
    activity_json_dao = ActivitiesJsonDao('./V2/source/activities_data.json')
    activity_service = ActivityService(activity_json_dao)
    activity_dto = activity_service.get_by_id(id)
    #print(activity_dto)

    activity_json = {
        'id': activity_dto.id,
        'name': activity_dto.name,
        'description': activity_dto.description,
        'deleted': activity_dto.deleted,
        'status': activity_dto.status,
        'tenant_id': activity_dto.tenant_id,

    }
    #print(activity_json)

    return activity_json