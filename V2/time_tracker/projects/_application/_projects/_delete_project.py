import json
from http import HTTPStatus

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB as database


def delete_project(req: func.HttpRequest) -> func.HttpResponse:
    project_dao = _infrastructure.ProjectsSQLDao(database())
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.DeleteProjectUseCase(project_service)

    try:
        project_id = int(req.route_params.get("id"))
        deleted_project = use_case.delete_project(project_id)

        status_code, response = [
          HTTPStatus.NOT_FOUND, b"Not found"
        ] if not deleted_project else [HTTPStatus.OK, json.dumps(deleted_project.__dict__)]

        return func.HttpResponse(
            body=response,
            status_code=status_code,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype="application/json"
        )
