from time_entries._infrastructure import ActivitiesJsonDao
from time_entries._domain import ActivityService, _use_cases

import azure.functions as func
import json
import logging

JSON_PATH = (
    'time_entries/_infrastructure/_data_persistence/activities_data.json'
)


def delete_activity(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to delete an activity.'
    )
    activity_id = req.route_params.get('id')
    response = _delete(activity_id)
    status_code = 200 if response != b'Not found' else 404

    return func.HttpResponse(
        body=response, status_code=status_code, mimetype="application/json"
    )


def _delete(activity_id: str) -> str:
    activity_use_case = _use_cases.DeleteActivityUseCase(
        _create_activity_service(JSON_PATH)
    )
    activity = activity_use_case.delete_activity(activity_id)
    return json.dumps(activity.__dict__) if activity else b'Not found'


def _create_activity_service(path: str):
    activity_json = ActivitiesJsonDao(path)
    return ActivityService(activity_json)
