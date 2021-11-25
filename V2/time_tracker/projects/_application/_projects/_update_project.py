import dataclasses
import json
from http import HTTPStatus

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB as database


def update_project(req: func.HttpRequest) -> func.HttpResponse:
    project_dao = _infrastructure.ProjectsSQLDao(database())
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.UpdateProjectUseCase(project_service)

    try:
        project_id = int(req.route_params.get("id"))
        project_data = req.get_json()

        if not _validate_project(project_data):
            status_code = HTTPStatus.BAD_REQUEST
            response = b"Incorrect body"

        else:
            updated_project = use_case.update_project(project_id, project_data)
            status_code, response = [
              HTTPStatus.NOT_FOUND, b"Not found"
            ] if not updated_project else [HTTPStatus.OK, json.dumps(updated_project.__dict__)]

        return func.HttpResponse(
            body=response,
            status_code=status_code,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype="application/json",
        )
    except Exception as error:
        return func.HttpResponse(
            body=str(error).encode(),
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype="application/json",
        )


def _validate_project(project_data: dict) -> bool:
    project_keys = [field.name for field in dataclasses.fields(_domain.Project)]
    return all(key in project_keys for key in project_data.keys())
