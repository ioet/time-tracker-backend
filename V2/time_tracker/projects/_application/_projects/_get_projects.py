import json
import typing

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB
from time_tracker.utils.enums import ResponseEnums as enums


def get_projects(req: func.HttpRequest) -> func.HttpResponse:
    database = DB()
    project_dao = _infrastructure.ProjectsSQLDao(database)
    project_service = _domain.ProjectService(project_dao)

    project_id = req.route_params.get("id")

    try:
        if project_id:
            response = _get_by_id(int(project_id), project_service)
            if not response:
                return func.HttpResponse(
                    body=enums.NOT_FOUND.value.encode(),
                    status_code=enums.STATUS_NOT_FOUND.value,
                    mimetype=enums.MIME_TYPE.value
                )
        else:
            response = _get_all(project_service)

        return func.HttpResponse(
            body=json.dumps(response),
            status_code=enums.STATUS_OK.value,
            mimetype=enums.MIME_TYPE.value,
        )

    except ValueError:
        return func.HttpResponse(
            body=enums.INVALID_ID.value.encode(),
            status_code=enums.STATUS_BAD_REQUEST.value,
            mimetype=enums.MIME_TYPE.value
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
