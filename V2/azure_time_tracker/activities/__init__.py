from time_tracker.source.use_cases.use_case import get_all, get_by_id

import logging
import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to get an activity.'
    )
    activity_id = req.route_params.get('id')

    if activity_id:
        response = json.dumps(get_by_id(activity_id))
    else:
        response = json.dumps(get_all())

    return func.HttpResponse(
        body=response, status_code=200, mimetype="application/json"
    )
