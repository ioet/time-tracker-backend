from V2.source.daos.activities_json_dao import ActivitiesJsonDao
from V2.source.services.activity_service import ActivityService
from V2.source import use_cases
from flask_restplus import Resource
from http import HTTPStatus

JSON_PATH = './V2/source/activities_data.json'


class Activities(Resource):
    def get(self):
        activity_json = ActivitiesJsonDao(JSON_PATH)
        activity_service = ActivityService(activity_json)
        activities = use_cases.GetActivitiesUseCase(activity_service)
        return [activity.__dict__ for activity in activities.get_activities()]


class Activity(Resource):
    def get(self, activity_id: str):
        try:
            activity_json = ActivitiesJsonDao(JSON_PATH)
            activity_service = ActivityService(activity_json)
            activity = use_cases.GetActivityUseCase(activity_service)
            return activity.get_activity_by_id(activity_id).__dict__
        except AttributeError:
            return {'message': 'Activity not found'}, HTTPStatus.NOT_FOUND
