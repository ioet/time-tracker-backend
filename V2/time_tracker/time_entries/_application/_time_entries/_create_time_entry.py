import dataclasses
import json
import typing

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB


def create_time_entry(req: func.HttpRequest) -> func.HttpResponse:
    database = DB()
    time_entry_dao = _infrastructure.TimeEntriesSQLDao(database)
    time_entry_service = _domain.TimeEntryService(time_entry_dao)
    use_case = _domain._use_cases.CreateTimeEntryUseCase(time_entry_service)

    time_entry_data = req.get_json()

    validation_errors = _validate_time_entry(time_entry_data)
    if validation_errors:
        return func.HttpResponse(
            body=json.dumps(validation_errors), status_code=400, mimetype="application/json"
        )

    time_entry_to_create = _domain.TimeEntry(
      id=None,
      start_date=time_entry_data["start_date"],
      owner_id=time_entry_data["owner_id"],
      description=time_entry_data["description"],
      activity_id=time_entry_data["activity_id"],
      uri=time_entry_data["uri"],
      technologies=time_entry_data["technologies"],
      end_date=time_entry_data["end_date"],
      deleted=False,
      timezone_offset=time_entry_data["timezone_offset"],
      project_id=time_entry_data["project_id"]
    )

    created_time_entry = use_case.create_time_entry(time_entry_to_create)

    if not created_time_entry:
        return func.HttpResponse(
          body=json.dumps({'error': 'time_entry could not be created'}),
          status_code=500,
          mimetype="application/json"
        )

    return func.HttpResponse(
      body=json.dumps(created_time_entry.__dict__),
      status_code=201,
      mimetype="application/json"
    )


def _validate_time_entry(time_entry_data: dict) -> typing.List[str]:
    time_entry_fields = [field.name for field in dataclasses.fields(_domain.TimeEntry)]
    time_entry_fields.pop(8)
    missing_keys = [field for field in time_entry_fields if field not in time_entry_data]
    return [
        f'The {missing_key} key is missing in the input data'
        for missing_key in missing_keys
    ]
