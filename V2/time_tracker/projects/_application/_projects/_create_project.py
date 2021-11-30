import dataclasses
import json
import typing
from http import HTTPStatus

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB as database


def create_project(req: func.HttpRequest) -> func.HttpResponse:

    project_dao = _infrastructure.ProjectsSQLDao(database())
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.CreateProjectUseCase(project_service)

    project_data = req.get_json()

    validation_errors = _validate_project(project_data)
    if validation_errors:
        status_code = HTTPStatus.BAD_REQUEST
        response = json.dumps(validation_errors)
    else:
        project_to_create = _domain.Project(
          id=None,
          name=project_data["name"],
          description=project_data["description"],
          project_type_id=project_data["project_type_id"],
          customer_id=project_data["customer_id"],
          status=project_data["status"],
          deleted=False,
          technologies=project_data["technologies"],
          customer=None
        )

        created_project = use_case.create_project(project_to_create)

        status_code, response = [
            HTTPStatus.INTERNAL_SERVER_ERROR,  b"could not be created"
        ] if not created_project else [HTTPStatus.CREATED, json.dumps(created_project.__dict__)]

    return func.HttpResponse(
      body=response,
      status_code=status_code,
      mimetype="application/json"
    )


def _validate_project(project_data: dict) -> typing.List[str]:
    project_fields = [field.name for field in dataclasses.fields(_domain.Project)
                      if field.type != typing.Optional[field.type]]
    missing_keys = [field for field in project_fields if field not in project_data]
    return [
        f'The {missing_key} key is missing in the input data'
        for missing_key in missing_keys
    ]
