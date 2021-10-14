from time_tracker.source.daos.activities_json_dao import ActivitiesJsonDao
from time_tracker.source.services.activity_service import ActivityService
from time_tracker.source import use_cases

import logging
import json
import azure.functions as func

JSON_PATH = 'V2/azure_time_tracker/time_tracker/source/activities_data.json'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to get an activity.'
    )
    activity_id = req.route_params.get('id')
    status_code = 200

    if activity_id:
        activity_use_case = use_cases.GetActivityUseCase(
            create_activity_service(JSON_PATH)
        )
        activity = activity_use_case.get_activity_by_id(activity_id)
        if activity:
            response = json.dumps(activity.__dict__)
        else:
            response = b'Not Found'
            status_code = 404
    else:
        activities_use_case = use_cases.GetActivitiesUseCase(
            create_activity_service(JSON_PATH)
        )
        response = json.dumps(
            [
                activity.__dict__
                for activity in activities_use_case.get_activities()
            ]
        )

    return func.HttpResponse(
        body=response, status_code=status_code, mimetype="application/json"
    )


def create_activity_service(path: str):
    activity_json = ActivitiesJsonDao(path)
    return ActivityService(activity_json)
