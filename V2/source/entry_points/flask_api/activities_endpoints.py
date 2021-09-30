from flask_restplus import Resource

from V2.source import use_cases

class Activities(Resource):
    def get(self):
        activities_dto = use_cases.get_list_activities()
        activities = [activity_dto.__dict__ for activity_dto in activities_dto]
        return activities


class Activity(Resource):
   def get(self, activity_id: str):
       activity_dto = use_cases.get_activity_by_id(activity_id)
       activity = activity_dto.__dict__
       return activity