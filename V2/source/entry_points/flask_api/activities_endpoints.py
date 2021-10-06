from V2.source import use_cases
from flask_restplus import Resource
from http import HTTPStatus


class Activities(Resource):
    def get(self):
        activities_dto = use_cases.get_list_activities()
        activities = [activity_dto.__dict__ for activity_dto in activities_dto]
        return activities


class Activity(Resource):
    def get(self, activity_id: str):
        try:
            activities_dto = use_cases.get_activity_by_id(activity_id)
            activity = activities_dto.__dict__
            return activity
        except AttributeError:
            return {'message': 'Activity not found'}, HTTPStatus.NOT_FOUND
