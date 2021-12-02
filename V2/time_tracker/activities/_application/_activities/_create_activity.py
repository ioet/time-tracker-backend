import json
import dataclasses
import typing

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB
from time_tracker.utils.parsers import parse_status_to_string_for_ui as parse_status


def create_activity(req: func.HttpRequest) -> func.HttpResponse:
    database = DB()
    activity_dao = _infrastructure.ActivitiesSQLDao(database)
    activity_service = _domain.ActivityService(activity_dao)
    use_case = _domain._use_cases.CreateActivityUseCase(activity_service)

    activity_data = req.get_json()

    validation_errors = _validate_activity(activity_data)
    if validation_errors:
        return func.HttpResponse(
            body=json.dumps(validation_errors), status_code=400, mimetype="application/json"
        )

    activity_to_create = _domain.Activity(
        id=None,
        name=activity_data['name'],
        description=activity_data['description'],
        status=None,
        deleted=None
    )

    created_activity = use_case.create_activity(activity_to_create)
    if not create_activity:
        return func.HttpResponse(
            body={'error': 'activity could not be created'},
            status_code=500,
            mimetype="application/json",
        )
    return func.HttpResponse(
        body=json.dumps(parse_status(created_activity.__dict__)),
        status_code=201,
        mimetype="application/json"
    )


def _validate_activity(activity_data: dict) -> typing.List[str]:
    activity_fields = [field for field in dataclasses.fields(_domain.Activity)]
    missing_keys = [field.name for field in activity_fields
                    if (field.name not in activity_data) and (field.type != typing.Optional[field.type])]
    return [
        f'The {missing_key} key is missing in the input data'
        for missing_key in missing_keys
    ]
