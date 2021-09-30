from flask_restplus import Resource

from V2.source.use_cases.get_activities_use_case import get_list_activities
from V2.source.use_cases.get_activity_by_id_use_case import get_activity_by_id
from V2.source.entry_points.flask_api.api import api

app = api.namespace(
    'activities',
    description='Namespace of the API for activities'
)

@app.route('/')
class Activities(Resource):
    def get(self):
        return get_list_activities()

@app.route('/<string:id>')
class Activity(Resource):
    def get(self, id: str):
        return get_activity_by_id(id)