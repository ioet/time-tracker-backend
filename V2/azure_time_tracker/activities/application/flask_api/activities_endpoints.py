from activities.infrastructure import ActivitiesJsonDao
from activities.domain import ActivityService
from activities.domain import use_cases
from flask_restplus import Resource
from http import HTTPStatus

JSON_PATH = 'V2/azure_time_tracker/activities/infrastructure/data_persistence/activities_data.json'


class Activities(Resource):
    def get(self):
        activities = use_cases.GetActivitiesUseCase(
            create_activity_service(JSON_PATH)
        )
        return [activity.__dict__ for activity in activities.get_activities()]


class Activity(Resource):
    def get(self, activity_id: str):
        try:
            activity = use_cases.GetActivityUseCase(
                create_activity_service(JSON_PATH)
            )
            return activity.get_activity_by_id(activity_id).__dict__
        except AttributeError:
            return {'message': 'Activity not found'}, HTTPStatus.NOT_FOUND


def create_activity_service(path: str):
    activity_json = ActivitiesJsonDao(path)
    return ActivityService(activity_json)
