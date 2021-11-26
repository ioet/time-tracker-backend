import json
import typing
from http import HTTPStatus

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB as database


def get_projects(req: func.HttpRequest) -> func.HttpResponse:
    project_dao = _infrastructure.ProjectsSQLDao(database())
    project_service = _domain.ProjectService(project_dao)

    project_id = req.route_params.get("id")

    try:
        if project_id:
            response = _get_by_id(int(project_id), project_service)
            if not response:
                return func.HttpResponse(
                    body=b"Not found",
                    status_code=HTTPStatus.NOT_FOUND,
                    mimetype="application/json"
                )
        else:
            response = _get_all(project_service)

        return func.HttpResponse(
            body=json.dumps(response),
            status_code=HTTPStatus.OK,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype="application/json"
        )


def _get_by_id(project_id: int, project_service: _domain.ProjectService) -> str:
    use_case = _domain._use_cases.GetProjectUseCase(project_service)
    project = use_case.get_project_by_id(project_id)

    return project.__dict__ if project else None


def _get_all(project_service: _domain.ProjectService) -> typing.List:
    use_case = _domain._use_cases.GetProjectsUseCase(project_service)
    return [
            project.__dict__
            for project in use_case.get_projects()
    ]
