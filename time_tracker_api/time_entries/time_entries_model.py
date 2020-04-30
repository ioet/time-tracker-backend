import abc
from dataclasses import dataclass, field
from typing import List, Callable

from azure.cosmos import PartitionKey
from flask_restplus._http import HTTPStatus

from commons.data_access_layer.cosmos_db import CosmosDBDao, CosmosDBRepository, CustomError, current_datetime_str, \
    CosmosDBModel, get_date_range_of_month, get_current_year, get_current_month
from commons.data_access_layer.database import CRUDDao
from time_tracker_api.security import current_user_id


class TimeEntriesDao(CRUDDao):
    @staticmethod
    def current_user_id():
        return current_user_id()

    @abc.abstractmethod
    def find_running(self):
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

    @staticmethod
    def create_sql_date_range_filter(date_range: dict) -> str:
        if 'start_date' and 'end_date' in date_range:
            return """
            ((c.start_date BETWEEN @start_date AND @end_date) OR
             (c.end_date BETWEEN @start_date AND @end_date))
            """
        else:
            return ''

    def find_all(self, partition_key_value: str, conditions: dict, date_range: dict):
        custom_sql_conditions = []
        custom_sql_conditions.append(
            self.create_sql_date_range_filter(date_range)
        )

        custom_params = self.generate_params(date_range)

        return CosmosDBRepository.find_all(
            self,
            partition_key_value=partition_key_value,
            conditions=conditions,
            custom_sql_conditions=custom_sql_conditions,
            custom_params=custom_params
        )

    def on_create(self, new_item_data: dict):
        CosmosDBRepository.on_create(self, new_item_data)

        if new_item_data.get("start_date") is None:
            new_item_data['start_date'] = current_datetime_str()

        self.validate_data(new_item_data)

    def on_update(self, updated_item_data: dict):
        CosmosDBRepository.on_update(self, updated_item_data)
        self.validate_data(updated_item_data)
        self.replace_empty_value_per_none(updated_item_data)

    def find_interception_with_date_range(self, start_date, end_date, owner_id, partition_key_value,
                                          ignore_id=None, visible_only=True, mapper: Callable = None):
        conditions = {
            "owner_id": owner_id,
            "tenant_id": partition_key_value,
        }
        params = [
            {"name": "@start_date", "value": start_date},
            {"name": "@end_date", "value": end_date or current_datetime_str()},
            {"name": "@ignore_id", "value": ignore_id},
        ]
        params.extend(self.generate_params(conditions))
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
            partition_key=partition_key_value)

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def find_running(self, partition_key_value: str, owner_id: str, mapper: Callable = None):
        conditions = {
            "owner_id": owner_id,
            "tenant_id": partition_key_value,
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
            parameters=self.generate_params(conditions),
            partition_key=partition_key_value,
            max_item_count=1)

        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(next(result))

    def validate_data(self, data):
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

    def get_all(self, conditions: dict = {}) -> list:
        conditions.update({"owner_id": self.current_user_id()})

        if 'month' and 'year' in conditions:
            month = int(conditions.get("month"))
            year = int(conditions.get("year"))
            conditions.pop('month')
            conditions.pop('year')
        elif 'month' in conditions:
            month = int(conditions.get("month"))
            year = get_current_year()
            conditions.pop('month')
        else:
            month = get_current_month()
            year = get_current_year()

        start_date, end_date = get_date_range_of_month(year, month)

        date_range = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        }
        return self.repository.find_all(partition_key_value=self.partition_key_value,
                                        conditions=conditions,
                                        date_range=date_range)

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

    def find_running(self):
        return self.repository.find_running(partition_key_value=self.partition_key_value,
                                            owner_id=self.current_user_id())


def create_dao() -> TimeEntriesDao:
    repository = TimeEntryCosmosDBRepository()

    return TimeEntriesCosmosDBDao(repository)
