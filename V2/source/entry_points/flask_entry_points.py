from flask import Flask
from flask_restplus import Resource, Api
from V2.source.use_cases.get_activities_use_case import get_list_activities
from V2.source.use_cases.get_activity_by_id_use_case import get_activity_by_id

app = Flask(__name__)
api = Api(app)

class Activities(Resource):
    def get(self):
        return get_list_activities()

class Activity(Resource):
    def get(self, id: str):
        return get_activity_by_id(id)

api.add_resource(Activities, '/activities')
api.add_resource(Activity, '/activity/<string:id>')