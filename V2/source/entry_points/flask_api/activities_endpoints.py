from V2.source import use_cases
from flask_restplus import Resource
from http import HTTPStatus


class Activities(Resource):
    def get(self):
        return [activity.__dict__ for activity in use_cases.get_list_activities()]


class Activity(Resource):
    def get(self, activity_id: str):
        try:
            return use_cases.get_activity_by_id(activity_id).__dict__
        except AttributeError:
            return {'message': 'Activity not found'}, HTTPStatus.NOT_FOUND
