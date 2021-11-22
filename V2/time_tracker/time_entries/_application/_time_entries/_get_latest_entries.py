import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB


def get_latest_entries(req: func.HttpRequest) -> func.HttpResponse:
    database = DB()
    time_entry_dao = _infrastructure.TimeEntriesSQLDao(database)
    time_entry_service = _domain.TimeEntryService(time_entry_dao)
    use_case = _domain._use_cases.GetLastestTimeEntryUseCase(time_entry_service)

    try:
        owner_id = req.params.get("owner_id")
        limit = req.params.get("limit")

        if not owner_id:
            return func.HttpResponse(
                body="No owner id found",
                status_code=404,
                mimetype="application/json"
            )

        time_entries = use_case.get_latest_entries(int(owner_id), int(limit) if limit and int(limit) > 0 else None)

        if not time_entries or len(time_entries) == 0:
            return func.HttpResponse(
                body="No time entries found",
                status_code=404,
                mimetype="application/json"
            )

        return func.HttpResponse(
            body=json.dumps(time_entries, default=str),
            status_code=200,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=400,
            mimetype="application/json"
        )
