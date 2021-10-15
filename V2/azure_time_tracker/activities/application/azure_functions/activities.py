from activities.infrastructure import ActivitiesJsonDao
from activities.domain import ActivityService
from activities.domain import Activity
from activities.domain import use_cases

import azure.functions as func
import json
import logging

JSON_PATH = 'activities/infrastructure/data_persistence/activities_data.json'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to get an activity.'
    )
    activity_id = req.route_params.get('id')
    status_code = 200

    if activity_id:
        response = get_by_id(activity_id)
        if response == b'Not Found':
            status_code = 404
    else:
        response = get_all()

    return func.HttpResponse(
        body=response, status_code=status_code, mimetype="application/json"
    )


def get_by_id(activity_id: str) -> str:
    activity_use_case = use_cases.GetActivityUseCase(
        create_activity_service(JSON_PATH)
    )
    activity = activity_use_case.get_activity_by_id(activity_id)

    return json.dumps(activity.__dict__) if activity else b'Not Found'


def get_all() -> str:
    activities_use_case = use_cases.GetActivitiesUseCase(
        create_activity_service(JSON_PATH)
    )
    return json.dumps(
        [
            activity.__dict__
            for activity in activities_use_case.get_activities()
        ]
    )


def create_activity_service(path: str):
    activity_json = ActivitiesJsonDao(path)
    return ActivityService(activity_json)
