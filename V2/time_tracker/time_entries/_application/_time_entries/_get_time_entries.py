import json
from http import HTTPStatus

import azure.functions as func

from time_tracker.time_entries._infrastructure import TimeEntriesSQLDao
from time_tracker.time_entries._domain import TimeEntryService, _use_cases
from time_tracker._infrastructure import DB


NOT_FOUND = b'Not Found'
INVALID_FORMAT_ID = b'Invalid Format ID'


def get_time_entries(req: func.HttpRequest) -> func.HttpResponse:

    time_entry_id = req.route_params.get('id')
    status_code = HTTPStatus.OK

    if time_entry_id:
        try:
            response = _get_by_id(int(time_entry_id))
            if response == NOT_FOUND:
                status_code = HTTPStatus.NOT_FOUND
        except ValueError:
            response = INVALID_FORMAT_ID
            status_code = HTTPStatus.BAD_REQUEST
    else:
        response = _get_all()

    return func.HttpResponse(
        body=response, status_code=status_code, mimetype="application/json"
    )


def _get_by_id(id: int) -> str:
    database = DB()
    time_entry_use_case = _use_cases.GetTimeEntryUseCase(
        _create_time_entry_service(database)
    )
    time_entry = time_entry_use_case.get_time_entry_by_id(id)

    return json.dumps(time_entry.__dict__) if time_entry else NOT_FOUND


def _get_all() -> str:
    database = DB()
    time_entries_use_case = _use_cases.GetTimeEntriesUseCase(
        _create_time_entry_service(database)
    )
    return json.dumps(
        [
            time_entry.__dict__
            for time_entry in time_entries_use_case.get_time_entries()
        ]
    )


def _create_time_entry_service(db: DB):
    time_entry_sql = TimeEntriesSQLDao(db)
    return TimeEntryService(time_entry_sql)
