import dataclasses
import json
import logging

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB

DATABASE = DB()


def update_activity(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to update an activity.'
    )
    try:
        activity_id = int(req.route_params.get('id'))
        activity_data = req.get_json() if req.get_body() else {}
        activity_keys = [field.name for field in dataclasses.fields(_domain.Activity)]

        if all(key in activity_keys for key in activity_data.keys()):
            response = _update(activity_id, activity_data)
            status_code = 200
        else:
            response = b'Incorrect activity body'
            status_code = 400

        return func.HttpResponse(
            body=response, status_code=status_code, mimetype="application/json"
        )
    except ValueError:
        return func.HttpResponse(
            body=b"Invalid format id", status_code=400, mimetype="application/json"
        )


def _update(activity_id: int, activity_data: dict) -> str:
    activity_use_case = _domain._use_cases.UpdateActivityUseCase(
        _create_activity_service(DATABASE)
    )
    activity = activity_use_case.update_activity(
        activity_id, activity_data.get("name"),
        activity_data.get("description"),
        activity_data.get("status"),
        activity_data.get("deleted")
        )
    return json.dumps(activity.__dict__) if activity else b'Not Found'


def _create_activity_service(db: DB) -> _domain.ActivityService:
    activity_sql = _infrastructure.ActivitiesSQLDao(db)
    return _domain.ActivityService(activity_sql)
