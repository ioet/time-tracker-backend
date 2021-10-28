from time_entries._infrastructure import ActivitiesJsonDao
from time_entries._domain import ActivityService, _use_cases, Activity

import azure.functions as func
import json
import logging
import dataclasses


JSON_PATH = (
    'time_entries/_infrastructure/_data_persistence/activities_data.json'
)



def create_activity(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to create an activity.'
    )
    activity_data = req.get_json()
    status_code = 200
    if _validate_activity(activity_data):
        response = _create_activity(activity_data)
    else:
        status_code = 404
        response = b'Not possible to create activity, attributes are not correct '

    return func.HttpResponse(
        body=response, status_code=status_code, mimetype="application/json"
    )

def _create_activity(activity_data: dict) -> str:
    activity_use_case = _use_cases.CreateActivityUseCase(
        _create_activity_service(JSON_PATH)
    )
    activity = activity_use_case.create_activity(activity_data)
    return json.dumps(activity.__dict__) if activity else b'Not Found'

def _validate_activity(activity_data: dict) -> bool:
    activity_keys = [field.name for field in dataclasses.fields(Activity)]
    new_activity_keys = list(activity_data.keys())
    return  all(map(lambda key: key in activity_keys, new_activity_keys)) and len(activity_keys) == len(new_activity_keys)

def _create_activity_service(path: str):
    activity_json = ActivitiesJsonDao(path)
    return ActivityService(activity_json)


