import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB

DATABASE = DB()


def delete_time_entry(req: func.HttpRequest) -> func.HttpResponse:
    time_entry_dao = _infrastructure.TimeEntriesSQLDao(DATABASE)
    time_entry_service = _domain.TimeEntryService(time_entry_dao)
    use_case = _domain._use_cases.DeleteTimeEntryUseCase(time_entry_service)

    try:
        time_entry_id = int(req.route_params.get("id"))
        deleted_time_entry = use_case.delete_time_entry(time_entry_id)
        if not deleted_time_entry:
            return func.HttpResponse(
                body="Not found",
                status_code=404,
                mimetype="application/json"
            )

        return func.HttpResponse(
            body=json.dumps(deleted_time_entry.__dict__, default=str),
            status_code=200,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=400,
            mimetype="application/json"
        )
