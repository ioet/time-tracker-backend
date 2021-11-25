import dataclasses
import json
import typing

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB as database
from time_tracker.utils.enums import ResponseEnums as enums


def create_project(req: func.HttpRequest) -> func.HttpResponse:

    project_dao = _infrastructure.ProjectsSQLDao(database())
    project_service = _domain.ProjectService(project_dao)
    use_case = _domain._use_cases.CreateProjectUseCase(project_service)

    project_data = req.get_json()

    validation_errors = _validate_project(project_data)
    if validation_errors:
        status_code = enums.STATUS_BAD_REQUEST.value
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
          technologies=project_data["technologies"]
        )

        created_project = use_case.create_project(project_to_create)

        status_code, response = [
            enums.INTERNAL_SERVER_ERROR.value, enums.NOT_CREATED.value.encode()
        ] if not created_project else [enums.STATUS_CREATED.value, json.dumps(created_project.__dict__)]

    return func.HttpResponse(
      body=response,
      status_code=status_code,
      mimetype=enums.MIME_TYPE.value
    )


def _validate_project(project_data: dict) -> typing.List[str]:
    project_fields = [field.name for field in dataclasses.fields(_domain.Project)
                      if field.type != typing.Optional[field.type]]
    missing_keys = [field for field in project_fields if field not in project_data]
    return [
        f'The {missing_key} key is missing in the input data'
        for missing_key in missing_keys
    ]
