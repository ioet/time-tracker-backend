import json
from http import HTTPStatus
import datetime

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB
from time_tracker.utils.enums import ResponseEnums


def get_time_entries_summary(req: func.HttpRequest) -> func.HttpResponse:
    database = DB()
    time_entry_dao = _infrastructure.TimeEntriesSQLDao(database)
    time_entry_service = _domain.TimeEntryService(time_entry_dao)
    use_case = _domain._use_cases.GetTimeEntriesSummaryUseCase(time_entry_service)

    response_params = {
        "body": ResponseEnums.NOT_FOUND.value,
        "status_code": HTTPStatus.NOT_FOUND,
        "mimetype": ResponseEnums.MIME_TYPE.value,
    }

    try:
        owner_id = req.params.get("owner_id")
        start_date = req.params.get("start_date")
        end_date = req.params.get("end_date")

        if not owner_id or not start_date or not end_date:
            return func.HttpResponse(**response_params)

        if not _validate_time_format(start_date) or not _validate_time_format(end_date):
            response_params["body"] = ResponseEnums.INVALID_DATE_FORMAT.value
            return func.HttpResponse(**response_params)

        time_entries = use_case.get_time_entries_summary(
            int(owner_id), start_date, end_date
        )

        if not time_entries:
            return func.HttpResponse(**response_params)

        response_params["body"] = json.dumps(time_entries, default=str)
        response_params["status_code"] = HTTPStatus.OK

        return func.HttpResponse(**response_params)

    except ValueError:
        response_params["body"] = ResponseEnums.INVALID_ID.value
        response_params["status_code"] = HTTPStatus.BAD_REQUEST
        return func.HttpResponse(**response_params)


def _validate_time_format(time: str) -> bool:
    try:
        datetime.datetime.strptime(time, "%m/%d/%Y")
    except ValueError:
        return False
    return True
