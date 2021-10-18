from time_entries.infrastructure import ActivitiesJsonDao
from time_entries.domain import ActivityService
from time_entries.domain import Activity
from time_entries.domain import use_cases

import azure.functions as func
import json
import logging

JSON_PATH = 'V2/azure_time_tracker/time_entries/infrastructure/data_persistence/activities_data.json'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to get an activity.'
    )
    activity_id = req.route_params.get('id')
    status_code = 200

    if activity_id:
        response = _get_by_id(activity_id)
        if response == b'Not Found':
            status_code = 404
    else:
        response = _get_all()

    return func.HttpResponse(
        body=response, status_code=status_code, mimetype="application/json"
    )


def _get_by_id(activity_id: str) -> str:
    activity_use_case = use_cases.GetActivityUseCase(
        _create_activity_service(JSON_PATH)
    )
    activity = activity_use_case.get_activity_by_id(activity_id)

    return json.dumps(activity.__dict__) if activity else b'Not Found'


def _get_all() -> str:
    activities_use_case = use_cases.GetActivitiesUseCase(
        _create_activity_service(JSON_PATH)
    )
    return json.dumps(
        [
            activity.__dict__
            for activity in activities_use_case.get_activities()
        ]
    )


def _create_activity_service(path: str):
    activity_json = ActivitiesJsonDao(path)
    return ActivityService(activity_json)
