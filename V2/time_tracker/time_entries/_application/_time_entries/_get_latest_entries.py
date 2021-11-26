import json
from http import HTTPStatus

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB
from time_tracker.utils.enums import ResponseEnums


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
                body=ResponseEnums.NOT_FOUND.value,
                status_code=HTTPStatus.NOT_FOUND,
                mimetype=ResponseEnums.MIME_TYPE.value,
            )

        time_entries = use_case.get_latest_entries(int(owner_id), int(limit) if limit and int(limit) > 0 else None)

        if not time_entries or len(time_entries) == 0:
            return func.HttpResponse(
                body=ResponseEnums.NOT_FOUND.value,
                status_code=HTTPStatus.NOT_FOUND,
                mimetype=ResponseEnums.MIME_TYPE.value,
            )

        return func.HttpResponse(
            body=json.dumps(time_entries, default=str),
            status_code=HTTPStatus.OK,
            mimetype=ResponseEnums.MIME_TYPE.value,
        )

    except ValueError:
        return func.HttpResponse(
            body=ResponseEnums.INVALID_ID.value,
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype=ResponseEnums.MIME_TYPE.value,
        )
