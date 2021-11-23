import dataclasses
import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB


def update_project(req: func.HttpRequest) -> func.HttpResponse:
    database = DB()
    project_dao = _infrastructure.ProjectsSQLDao(database)
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.UpdateProjectUseCase(project_service)

    try:
        project_id = int(req.route_params.get("id"))
        project_data = req.get_json()
        status_code = 200

        if not _validate_project(project_data):
            status_code = 400
            response = "Incorrect project body"

        response = use_case.update_project(project_id, project_data).__dict__

        if not update_project:
            status_code = 404
            response = "Not found"

        return func.HttpResponse(
            body=json.dumps(response, default=str),
            status_code=status_code,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=400,
            mimetype="application/json"
        )


def _validate_project(project_data: dict) -> bool:
    project_keys = [field.name for field in dataclasses.fields(_domain.Project)]
    return all(key in project_keys for key in project_data.keys())
