from time_entries._infrastructure import ActivitiesJsonDao
from time_entries._domain import ActivityService, Activity, _use_cases

import azure.functions as func
import dataclasses
import json
import logging

JSON_PATH = (
    'time_entries/_infrastructure/_data_persistence/activities_data.json'
)


def update_activity(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to update an activity.'
    )
    activity_id = req.route_params.get('id')
    activity_data = req.get_json() if req.get_body() else {}
    activity_keys = [field.name for field in dataclasses.fields(Activity)]

    if all(key in activity_keys for key in activity_data.keys()):
        response = _update(activity_id, activity_data)
        status_code = 200
    else:
        response = b'Incorrect activity body'
        status_code = 400

    return func.HttpResponse(
        body=response, status_code=status_code, mimetype="application/json"
    )


def _update(activity_id: str, activity_data: dict) -> str:
    activity_use_case = _use_cases.UpdateActivityUseCase(
        _create_activity_service(JSON_PATH)
    )
    activity = activity_use_case.update_activity(activity_id, activity_data)
    return json.dumps(activity.__dict__) if activity else b'Not Found'


def _create_activity_service(path: str):
    activity_json = ActivitiesJsonDao(path)
    return ActivityService(activity_json)
