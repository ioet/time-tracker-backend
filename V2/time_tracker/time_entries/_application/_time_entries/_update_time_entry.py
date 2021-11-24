import dataclasses
import json
import logging

import azure.functions as func

from time_tracker.time_entries._infrastructure import TimeEntriesSQLDao
from time_tracker.time_entries._domain import TimeEntryService, TimeEntry, _use_cases
from time_tracker._infrastructure import DB


def update_time_entry(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(
        'Python HTTP trigger function processed a request to update an time entry.'
    )
    time_entry_id = req.route_params.get('id')
    time_entry_data = req.get_json() if req.get_body() else {}
    time_entry_keys = [field.name for field in dataclasses.fields(TimeEntry)]

    if all(key in time_entry_keys for key in time_entry_data.keys()):
        try:
            response = _update(int(time_entry_id), time_entry_data)
            status_code = 200
        except ValueError:
            response = b'Invalid Format ID'
            status_code = 404
    else:
        response = b'Incorrect time entry body'
        status_code = 400

    return func.HttpResponse(
        body=response, status_code=status_code, mimetype="application/json"
    )


def _update(time_entry_id: int, time_entry_data: dict) -> str:
    database = DB()
    time_entry_use_case = _use_cases.UpdateTimeEntryUseCase(
        _create_time_entry_service(database)
    )
    time_entry = time_entry_use_case.update_time_entry(time_entry_id, time_entry_data)
    return json.dumps(time_entry.__dict__) if time_entry else b'Not Found'


def _create_time_entry_service(db: DB):
    time_entry_dao = TimeEntriesSQLDao(db)
    return TimeEntryService(time_entry_dao)
