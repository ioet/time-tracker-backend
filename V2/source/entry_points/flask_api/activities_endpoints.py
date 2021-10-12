from V2.source import use_cases
from flask_restplus import Resource
from http import HTTPStatus


class Activities(Resource):
    def get(self):
        activities = use_cases.GetActivitiesUseCase()
        return [activity.__dict__ for activity in activities.get_activities()]


class Activity(Resource):
    def get(self, activity_id: str):
        try:
            activity = use_cases.GetActivityUseCase()
            return activity.get_activity_by_id(activity_id).__dict__
        except AttributeError:
            return {'message': 'Activity not found'}, HTTPStatus.NOT_FOUND
