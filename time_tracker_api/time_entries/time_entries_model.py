import abc
from dataclasses import dataclass, field
from typing import List, Callable
from azure.cosmos import PartitionKey
from flask_restplus import abort
from flask_restplus._http import HTTPStatus

from datetime import timedelta

from commons.data_access_layer.cosmos_db import (
    CosmosDBDao,
    CosmosDBRepository,
    CustomError,
    CosmosDBModel,
)

from commons.data_access_layer.database import EventContext
from time_tracker_api.activities import activities_model

from utils.extend_model import (
    add_project_info_to_time_entries,
    add_activity_name_to_time_entries,
    create_in_condition,
    create_custom_query_from_str,
    add_user_email_to_time_entries,
)
from utils.time import (
    datetime_str,
    str_to_datetime,
    get_current_year,
    get_current_month,
    get_date_range_of_month,
    current_datetime_str,
)
from utils import worked_time
from utils.azure_users import AzureConnection

from time_tracker_api.projects.projects_model import ProjectCosmosDBModel
from time_tracker_api.projects import projects_model
from time_tracker_api.database import CRUDDao, APICosmosDBDao

container_definition = {
    'id': 'time_entry',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [{'paths': ['/owner_id', '/end_date', '/deleted']}]
    },
}


@dataclass()
class TimeEntryCosmosDBModel(CosmosDBModel):
    project_id: str
    start_date: str
    owner_id: str
    id: str
    tenant_id: str
    description: str = field(default=None)
    activity_id: str = field(default=None)
    uri: str = field(default=None)
    technologies: List[str] = field(default_factory=list)
    end_date: str = field(default=None)
    deleted: str = field(default=None)
    timezone_offset: str = field(default=None)

    def __init__(self, data):  # pragma: no cover
        super(TimeEntryCosmosDBModel, self).__init__(data)

    @property
    def running(self):
        return self.end_date is None

    @property
    def elapsed_time(self) -> timedelta:
        start_datetime = str_to_datetime(self.start_date)
        end_datetime = str_to_datetime(self.end_date)
        return end_datetime - start_datetime

    def __add__(self, other):
        if type(other) is ProjectCosmosDBModel:
            time_entry = self.__class__
            time_entry.project_id = other.__dict__
            return time_entry
        else:
            raise NotImplementedError

    def __repr__(self):
        return f'<Time Entry {self.start_date} - {self.end_date}>'  # pragma: no cover

    def __str___(self):
        return (
            "Time Entry started in \"%s\"" % self.start_date
        )  # pragma: no cover
