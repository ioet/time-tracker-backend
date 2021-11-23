import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB


def delete_project(req: func.HttpRequest) -> func.HttpResponse:
    project_dao = _infrastructure.ProjectsSQLDao(DB())
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.DeleteProjectUseCase(project_service)

    try:
        project_id = int(req.route_params.get("id"))
        deleted_project = use_case.delete_project(project_id)
        if not deleted_project:
            return func.HttpResponse(
                body="Not found",
                status_code=404,
                mimetype="application/json"
            )

        return func.HttpResponse(
            body=json.dumps(deleted_project.__dict__, default=str),
            status_code=200,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=400,
            mimetype="application/json"
        )
