import dataclasses
import json
import typing

import azure.functions as func

from ... import _domain
from ... import _infrastructure

_JSON_PATH = (
    'time_entries/_infrastructure/_data_persistence/time_entries_data.json'
)

def create_time_entry(req: func.HttpRequest) -> func.HttpResponse:

  time_entry_dao = _infrastructure.TimeEntriesJsonDao(_JSON_PATH)
  time_entry_service = _domain.TimeEntryService(time_entry_dao)
  use_case = _domain._use_cases.CreateTimeEntryUseCase(time_entry_service)

  time_entry_data = req.get_json()

  time_entry_to_create = _domain.TimeEntry(
    id=None,
    start_date=time_entry_data["start_date"],
    owner_id=time_entry_data["owner_id"],
    description=time_entry_data["description"],
    activity_id=time_entry_data["activity_id"],
    uri=time_entry_data["uri"],
    technologies=time_entry_data["technologies"],
    end_date=time_entry_data["end_date"],
    deleted=time_entry_data["deleted"],
    timezone_offset=time_entry_data["timezone_offset"],
    project_id=time_entry_data["project_id"]
  )

  created_time_entry = use_case.create_time_entry(time_entry_to_create.__dict__)
  
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