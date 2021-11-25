import dataclasses
import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB as database
from time_tracker.utils.enums import ResponseEnums as enums


def update_project(req: func.HttpRequest) -> func.HttpResponse:
    project_dao = _infrastructure.ProjectsSQLDao(database())
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.UpdateProjectUseCase(project_service)

    try:
        project_id = int(req.route_params.get("id"))
        project_data = req.get_json()

        if not _validate_project(project_data):
            status_code = enums.STATUS_BAD_REQUEST.value
            response = enums.INCORRECT_BODY.value.encode()

        else:
            updated_project = use_case.update_project(project_id, project_data)
            status_code, response = [
              enums.STATUS_NOT_FOUND.value, enums.NOT_FOUND.value.encode()
            ] if not updated_project else [enums.STATUS_OK.value, json.dumps(updated_project.__dict__)]

        return func.HttpResponse(
            body=response,
            status_code=status_code,
            mimetype=enums.MIME_TYPE.value,
        )

    except ValueError:
        return func.HttpResponse(
            body=enums.INVALID_ID.value.encode(),
            status_code=enums.STATUS_BAD_REQUEST.value,
            mimetype=enums.MIME_TYPE.value,
        )
    except Exception as error:
        return func.HttpResponse(
            body=str(error).encode(),
            status_code=enums.STATUS_BAD_REQUEST.value,
            mimetype=enums.MIME_TYPE.value,
        )


def _validate_project(project_data: dict) -> bool:
    project_keys = [field.name for field in dataclasses.fields(_domain.Project)]
    return all(key in project_keys for key in project_data.keys())
