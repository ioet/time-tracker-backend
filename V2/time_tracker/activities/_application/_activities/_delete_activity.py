import json
import logging

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB

DATABASE = DB()


def delete_activity(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to delete an activity.'
    )
    try:
        activity_id = int(req.route_params.get('id'))
        response = _delete(activity_id)
        status_code = 200 if response != b'Not found' else 404

        return func.HttpResponse(
            body=response, status_code=status_code, mimetype="application/json"
        )
    except ValueError:
        return func.HttpResponse(
            body=b"Invalid format id", status_code=400, mimetype="application/json"
        )


def _delete(activity_id: int) -> str:
    activity_use_case = _domain._use_cases.DeleteActivityUseCase(
        _create_activity_service(DATABASE)
    )
    activity = activity_use_case.delete_activity(activity_id)
    return json.dumps(activity.__dict__) if activity else b'Not found'


def _create_activity_service(db: DB) -> _domain.ActivityService:
    activity_sql = _infrastructure.ActivitiesSQLDao(db)
    return _domain.ActivityService(activity_sql)
