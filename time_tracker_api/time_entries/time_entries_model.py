from dataclasses import dataclass, field
from typing import List, Callable

from azure.cosmos import PartitionKey
from flask_restplus._http import HTTPStatus

from commons.data_access_layer.cosmos_db import CosmosDBDao, CosmosDBRepository, CustomError, CosmosDBModel, \
    current_datetime, datetime_str
from commons.data_access_layer.database import CRUDDao
from time_tracker_api.security import current_user_id


class TimeEntriesDao(CRUDDao):
    @staticmethod
    def current_user_id():
        return current_user_id()


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
    id: str
    description: str
    project_id: str
    activity_id: str
    owner_id: str
    tenant_id: str
    uri: str = field(default=None)
    technologies: List[str] = field(default_factory=list)
    start_date: str = field(default_factory=current_datetime)
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

    def on_create(self, new_item_data: dict):
        CosmosDBRepository.on_create(self, new_item_data)
        self.validate_data(new_item_data)

    def on_update(self, updated_item_data: dict):
        CosmosDBRepository.on_update(self, updated_item_data)
        self.validate_data(updated_item_data)

    def find_interception_with_date_range(self, start_date, end_date, owner_id, partition_key_value,
                                          ignore_id=None, visible_only=True, mapper: Callable = None):
        conditions = {"owner_id": owner_id}
        params = self.append_conditions_values([
            {"name": "@partition_key_value", "value": partition_key_value},
            {"name": "@start_date", "value": start_date},
            {"name": "@end_date", "value": end_date or datetime_str(current_datetime())},
            {"name": "@ignore_id", "value": ignore_id},
        ], conditions)
        result = self.container.query_items(
            query="""
            SELECT * FROM c WHERE c.tenant_id=@partition_key_value  
             AND ((c.start_date BETWEEN @start_date AND @end_date) OR (c.end_date BETWEEN @start_date AND @end_date))
             {conditions_clause} {ignore_id_condition} {visibility_condition} {order_clause}
            """.format(partition_key_attribute=self.partition_key_attribute,
                       ignore_id_condition=self.create_sql_ignore_id_condition(ignore_id),
                       visibility_condition=self.create_sql_condition_for_visibility(visible_only),
                       conditions_clause=self.create_sql_where_conditions(conditions),
                       order_clause=self.create_sql_order_clause()),
            parameters=params,
            partition_key=partition_key_value)

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def validate_data(self, data):
        if data.get('end_date') is not None:
            if data['end_date'] <= data.get('start_date'):
                raise CustomError(HTTPStatus.BAD_REQUEST,
                                  description="You must end the time entry after it started")
            if data['end_date'] >= datetime_str(current_datetime()):
                raise CustomError(HTTPStatus.BAD_REQUEST,
                                  description="You cannot end a time entry in the future")

        collision = self.find_interception_with_date_range(start_date=data.get('start_date'),
                                                           end_date=data.get('end_date'),
                                                           owner_id=data.get('owner_id'),
                                                           partition_key_value=data.get('tenant_id'),
                                                           ignore_id=data.get('id'))
        if len(collision) > 0:
            raise CustomError(HTTPStatus.UNPROCESSABLE_ENTITY,
                              description="There is another time entry in that date range")


class TimeEntriesCosmosDBDao(TimeEntriesDao, CosmosDBDao):
    def __init__(self, repository):
        CosmosDBDao.__init__(self, repository)

    @classmethod
    def check_whether_current_user_owns_item(cls, data: dict):
        if data.get('owner_id') is not None \
                and data.get('owner_id') != cls.current_user_id():
            raise CustomError(HTTPStatus.FORBIDDEN,
                              "The current user is not the owner of this time entry")

    def get_all(self) -> list:
        return self.repository.find_all(partition_key_value=self.partition_key_value,
                                        conditions={"owner_id": self.current_user_id()})

    def get(self, id):
        return self.repository.find(id,
                                    partition_key_value=self.partition_key_value,
                                    peeker=self.check_whether_current_user_owns_item)

    def create(self, data: dict):
        data[self.repository.partition_key_attribute] = self.partition_key_value
        data["owner_id"] = self.current_user_id()
        return self.repository.create(data)

    def update(self, id, data: dict):
        return self.repository.partial_update(id,
                                              changes=data,
                                              partition_key_value=self.partition_key_value,
                                              peeker=self.check_whether_current_user_owns_item)

    def delete(self, id):
        self.repository.delete(id, partition_key_value=self.partition_key_value,
                               peeker=self.check_whether_current_user_owns_item)


def create_dao() -> TimeEntriesDao:
    repository = TimeEntryCosmosDBRepository()

    return TimeEntriesCosmosDBDao(repository)
