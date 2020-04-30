import abc
from dataclasses import dataclass, field
from typing import List, Callable

from azure.cosmos import PartitionKey
from flask_restplus._http import HTTPStatus

from commons.data_access_layer.cosmos_db import CosmosDBDao, CosmosDBRepository, CustomError, current_datetime_str, \
    CosmosDBModel
from commons.data_access_layer.database import EventContext
from time_tracker_api.database import CRUDDao, APICosmosDBDao
from time_tracker_api.security import current_user_id


class TimeEntriesDao(CRUDDao):
    @staticmethod
    def current_user_id():
        return current_user_id()

    @abc.abstractmethod
    def find_running(self):
        pass

    @abc.abstractmethod
    def stop(self, id: str):
        pass

    @abc.abstractmethod
    def restart(self, id: str):
        pass


container_definition = {
    'id': 'time_entry',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/owner_id', '/end_date', '/deleted']},
        ]
    }
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

    def __init__(self, data):  # pragma: no cover
        super(TimeEntryCosmosDBModel, self).__init__(data)

    @property
    def running(self):
        return self.end_date is None

    def __repr__(self):
        return '<Time Entry %r>' % self.start_date  # pragma: no cover

    def __str___(self):
        return "Time Entry started in \"%s\"" % self.start_date  # pragma: no cover


class TimeEntryCosmosDBRepository(CosmosDBRepository):
    def __init__(self):
        CosmosDBRepository.__init__(self, container_id=container_definition['id'],
                                    partition_key_attribute='tenant_id',
                                    order_fields=['start_date DESC'],
                                    mapper=TimeEntryCosmosDBModel)

    @staticmethod
    def create_sql_ignore_id_condition(id: str):
        if id is None:
            return ''
        else:
            return "AND c.id!=@ignore_id"

    def on_create(self, new_item_data: dict, event_context: EventContext):
        CosmosDBRepository.on_create(self, new_item_data, event_context)

        if new_item_data.get("start_date") is None:
            new_item_data['start_date'] = current_datetime_str()

        self.validate_data(new_item_data, event_context)

    def on_update(self, updated_item_data: dict, event_context: EventContext):
        CosmosDBRepository.on_update(self, updated_item_data, event_context)
        self.validate_data(updated_item_data, event_context)
        self.replace_empty_value_per_none(updated_item_data)

    def find_interception_with_date_range(self, start_date, end_date, owner_id, tenant_id,
                                          ignore_id=None, visible_only=True, mapper: Callable = None):
        conditions = {
            "owner_id": owner_id,
            "tenant_id": tenant_id,
        }
        params = [
            {"name": "@start_date", "value": start_date},
            {"name": "@end_date", "value": end_date or current_datetime_str()},
            {"name": "@ignore_id", "value": ignore_id},
        ]
        params.extend(self.generate_condition_values(conditions))
        result = self.container.query_items(
            query="""
            SELECT * FROM c WHERE ((c.start_date BETWEEN @start_date AND @end_date) 
              OR (c.end_date BETWEEN @start_date AND @end_date))
             {conditions_clause} {ignore_id_condition} {visibility_condition} {order_clause}
            """.format(ignore_id_condition=self.create_sql_ignore_id_condition(ignore_id),
                       visibility_condition=self.create_sql_condition_for_visibility(visible_only),
                       conditions_clause=self.create_sql_where_conditions(conditions),
                       order_clause=self.create_sql_order_clause()),
            parameters=params,
            partition_key=tenant_id)

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def find_running(self, tenant_id: str, owner_id: str, mapper: Callable = None):
        conditions = {
            "owner_id": owner_id,
            "tenant_id": tenant_id,
        }
        result = self.container.query_items(
            query="""
                  SELECT * from c
                  WHERE (NOT IS_DEFINED(c.end_date) OR c.end_date = null) 
                  {conditions_clause} {visibility_condition}
                  OFFSET 0 LIMIT 1
            """.format(
                visibility_condition=self.create_sql_condition_for_visibility(True),
                conditions_clause=self.create_sql_where_conditions(conditions),
            ),
            parameters=self.generate_condition_values(conditions),
            partition_key=tenant_id,
            max_item_count=1)

        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(next(result))

    def validate_data(self, data, event_context: EventContext):
        start_date = data.get('start_date')

        if data.get('end_date') is not None:
            if data['end_date'] <= start_date:
                raise CustomError(HTTPStatus.BAD_REQUEST,
                                  description="You must end the time entry after it started")
            if data['end_date'] >= current_datetime_str():
                raise CustomError(HTTPStatus.BAD_REQUEST,
                                  description="You cannot end a time entry in the future")

        collision = self.find_interception_with_date_range(start_date=start_date,
                                                           end_date=data.get('end_date'),
                                                           owner_id=event_context.user_id,
                                                           tenant_id=event_context.tenant_id,
                                                           ignore_id=data.get('id'))
        if len(collision) > 0:
            raise CustomError(HTTPStatus.UNPROCESSABLE_ENTITY,
                              description="There is another time entry in that date range")


class TimeEntriesCosmosDBDao(APICosmosDBDao, TimeEntriesDao):
    def __init__(self, repository):
        CosmosDBDao.__init__(self, repository)

    @classmethod
    def check_whether_current_user_owns_item(cls, data: dict):
        if data.get('owner_id') is not None \
                and data.get('owner_id') != cls.current_user_id():
            raise CustomError(HTTPStatus.FORBIDDEN,
                              "The current user is not the owner of this time entry")

    @classmethod
    def checks_owner_and_is_not_stopped(cls, data: dict):
        cls.check_whether_current_user_owns_item(data)

        if data.get('end_date') is not None:
            raise CustomError(HTTPStatus.UNPROCESSABLE_ENTITY, "The specified time entry is already stopped")

    @classmethod
    def checks_owner_and_is_not_started(cls, data: dict):
        cls.check_whether_current_user_owns_item(data)

        if data.get('end_date') is None:
            raise CustomError(HTTPStatus.UNPROCESSABLE_ENTITY, "The specified time entry is already running")

    def get_all(self, conditions: dict = {}) -> list:
        event_ctx = self.create_event_context("read-many")
        conditions.update({"owner_id": event_ctx.user_id})
        return self.repository.find_all(event_ctx, conditions=conditions)

    def get(self, id):
        event_ctx = self.create_event_context("read")
        return self.repository.find(id, event_ctx, peeker=self.check_whether_current_user_owns_item)

    def create(self, data: dict):
        event_ctx = self.create_event_context("create")
        return self.repository.create(data, event_ctx)

    def update(self, id, data: dict, description=None):
        event_ctx = self.create_event_context("update", description)
        return self.repository.partial_update(id, data, event_ctx,
                                              peeker=self.check_whether_current_user_owns_item)

    def stop(self, id):
        event_ctx = self.create_event_context("update", "Stop time entry")
        return self.repository.partial_update(id, {
            'end_date': current_datetime_str()
        }, event_ctx, peeker=self.checks_owner_and_is_not_stopped)

    def restart(self, id):
        event_ctx = self.create_event_context("update", "Restart time entry")
        return self.repository.partial_update(id, {
            'end_date': None
        }, event_ctx, peeker=self.checks_owner_and_is_not_started)

    def delete(self, id):
        event_ctx = self.create_event_context("delete")
        self.repository.delete(id, event_ctx, peeker=self.check_whether_current_user_owns_item)

    def find_running(self):
        event_ctx = self.create_event_context("find_running")
        return self.repository.find_running(event_ctx.tenant_id, event_ctx.user_id)


def create_dao() -> TimeEntriesDao:
    repository = TimeEntryCosmosDBRepository()

    return TimeEntriesCosmosDBDao(repository)
