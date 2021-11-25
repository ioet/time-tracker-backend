import dataclasses
import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB


def update_time_entry(req: func.HttpRequest) -> func.HttpResponse:
    database = DB()
    time_entry_dao = _infrastructure.TimeEntriesSQLDao(database)
    time_entry_service = _domain.TimeEntryService(time_entry_dao)
    use_case = _domain._use_cases.UpdateTimeEntryUseCase(time_entry_service)

    try:
        time_entry_id = int(req.route_params.get("id"))
        time_entry_data = req.get_json()

        if not _validate_time_entry(time_entry_data):
            status_code = 400
            response = b"Incorrect time entry body"
        else:
            updated_time_entry = use_case.update_time_entry(time_entry_id, time_entry_data)
            status_code, response = [
                404, b"Not found"
            ] if not updated_time_entry else [200, json.dumps(updated_time_entry.__dict__)]

        return func.HttpResponse(
            body=response,
            status_code=status_code,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=400,
            mimetype="application/json"
        )


def _validate_time_entry(time_entry_data: dict) -> bool:
    time_entry_keys = [field.name for field in dataclasses.fields(_domain.TimeEntry)]
    return all(key in time_entry_keys for key in time_entry_data.keys())
