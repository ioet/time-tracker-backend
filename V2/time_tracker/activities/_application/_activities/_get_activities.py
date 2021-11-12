import json
import logging

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB

DATABASE = DB()


def get_activities(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to get an activity.'
    )
    activity_id = req.route_params.get('id')
    status_code = 200

    try:
        if activity_id:
            response = _get_by_id(int(activity_id))
            if response == b'Not Found':
                status_code = 404
        else:
            response = _get_all()

        return func.HttpResponse(
            body=response, status_code=status_code, mimetype="application/json"
        )
    except ValueError:
        return func.HttpResponse(
            body=b"Invalid format id", status_code=400, mimetype="application/json"
        )


def _get_by_id(activity_id: int) -> str:
    activity_use_case = _domain._use_cases.GetActivityUseCase(
        _create_activity_service(DATABASE)
    )
    activity = activity_use_case.get_activity_by_id(activity_id)

    return json.dumps(activity.__dict__) if activity else b'Not Found'


def _get_all() -> str:
    activities_use_case = _domain._use_cases.GetActivitiesUseCase(
        _create_activity_service(DATABASE)
    )
    return json.dumps(
        [
            activity.__dict__
            for activity in activities_use_case.get_activities()
        ]
    )


def _create_activity_service(db: DB) -> _domain.ActivityService:
    activity_sql = _infrastructure.ActivitiesSQLDao(db)
    return _domain.ActivityService(activity_sql)
