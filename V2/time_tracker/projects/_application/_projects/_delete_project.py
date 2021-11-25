import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB as database
from time_tracker.utils.enums import ResponseEnums as enums


def delete_project(req: func.HttpRequest) -> func.HttpResponse:
    project_dao = _infrastructure.ProjectsSQLDao(database())
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.DeleteProjectUseCase(project_service)

    try:
        project_id = int(req.route_params.get("id"))
        deleted_project = use_case.delete_project(project_id)

        status_code, response = [
          enums.STATUS_NOT_FOUND.value, enums.NOT_FOUND.value.encode()
        ] if not deleted_project else [enums.STATUS_OK.value, json.dumps(deleted_project.__dict__)]

        return func.HttpResponse(
            body=response,
            status_code=status_code,
            mimetype=enums.MIME_TYPE.value,
        )

    except ValueError:
        return func.HttpResponse(
            body=enums.INVALID_ID.value.encode(),
            status_code=enums.STATUS_BAD_REQUEST.value,
            mimetype=enums.MIME_TYPE.value
        )
