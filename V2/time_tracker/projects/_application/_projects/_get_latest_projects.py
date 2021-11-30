import json
from http import HTTPStatus

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB as database


def get_latest_projects(req: func.HttpRequest) -> func.HttpResponse:
    project_dao = _infrastructure.ProjectsSQLDao(database())
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.GetLatestProjectsUseCase(project_service)

    owner_id = req.params.get('owner_id')
    response = [
            project.__dict__
            for project in use_case.get_latest(owner_id)
    ]

    return func.HttpResponse(
        body=json.dumps(response),
        status_code=HTTPStatus.OK,
        mimetype="application/json",
    )
