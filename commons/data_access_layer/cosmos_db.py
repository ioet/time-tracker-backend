import dataclasses
import logging
import uuid
from datetime import datetime
from typing import Callable

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import ContainerProxy, PartitionKey
from flask import Flask
from werkzeug.exceptions import HTTPException

from commons.data_access_layer.database import CRUDDao, EventContext


class CosmosDBFacade:
    def __init__(self, client, db_id: str, logger=None):  # pragma: no cover
        self.client = client
        self.db = self.client.get_database_client(db_id)
        if logger is None:
            self.logger = logging.getLogger(CosmosDBFacade.__name__)
        else:
            self.logger = logger

    @classmethod
    def from_flask_config(cls, app: Flask):
        db_uri = app.config.get('COSMOS_DATABASE_URI')
        if db_uri is None:
            app.logger.warn("COSMOS_DATABASE_URI was not found. Looking for alternative variables.")
            account_uri = app.config.get('DATABASE_ACCOUNT_URI')
            if account_uri is None:
                raise EnvironmentError("DATABASE_ACCOUNT_URI is not defined in the environment")

            master_key = app.config.get('DATABASE_MASTER_KEY')
            if master_key is None:
                raise EnvironmentError("DATABASE_MASTER_KEY is not defined in the environment")

            client = cosmos_client.CosmosClient(account_uri, {'masterKey': master_key},
                                                user_agent="TimeTrackerAPI",
                                                user_agent_overwrite=True)
        else:
            client = cosmos_client.CosmosClient.from_connection_string(db_uri)

        db_id = app.config.get('DATABASE_NAME')
        if db_id is None:
            raise EnvironmentError("DATABASE_NAME is not defined in the environment")

        return cls(client, db_id, logger=app.logger)

    def create_container(self, container_definition: dict):
        return self.db.create_container(**container_definition)

    def create_container_if_not_exists(self, container_definition: dict):
        return self.db.create_container_if_not_exists(**container_definition)

    def delete_container(self, container_id: str):
        return self.db.delete_container(container_id)


cosmos_helper: CosmosDBFacade = None


class CosmosDBModel():
    def __init__(self, data):
        names = set([f.name for f in dataclasses.fields(self)])
        for k, v in data.items():
            if k in names:
                setattr(self, k, v)


def partition_key_attribute(pk: PartitionKey) -> str:
    return pk.path.strip('/')


class CosmosDBRepository:
    def __init__(self, container_id: str,
                 partition_key_attribute: str,
                 mapper: Callable = None,
                 order_fields: list = [],
                 custom_cosmos_helper: CosmosDBFacade = None):
        global cosmos_helper
        self.cosmos_helper = custom_cosmos_helper or cosmos_helper
        if self.cosmos_helper is None:  # pragma: no cover
            raise ValueError("The cosmos_db module has not been initialized!")
        self.mapper = mapper
        self.order_fields = order_fields
        self.container: ContainerProxy = self.cosmos_helper.db.get_container_client(container_id)
        self.partition_key_attribute: str = partition_key_attribute

    @classmethod
    def from_definition(cls, container_definition: dict,
                        mapper: Callable = None,
                        custom_cosmos_helper: CosmosDBFacade = None):
        pk_attrib = partition_key_attribute(container_definition['partition_key'])
        return cls(container_definition['id'], pk_attrib,
                   mapper=mapper,
                   custom_cosmos_helper=custom_cosmos_helper)

    @staticmethod
    def create_sql_condition_for_visibility(visible_only: bool, container_name='c') -> str:
        if visible_only:
            # We are considering that `deleted == null` is not a choice
            return 'AND NOT IS_DEFINED(%s.deleted)' % container_name
        return ''

    @staticmethod
    def create_sql_where_conditions(conditions: dict, container_name='c') -> str:
        where_conditions = []
        for k in conditions.keys():
            where_conditions.append(f'{container_name}.{k} = @{k}')

        if len(where_conditions) > 0:
            return "AND {where_conditions_clause}".format(
                where_conditions_clause=" AND ".join(where_conditions))
        else:
            return ""

    @staticmethod
    def generate_condition_values(conditions: dict) -> dict:
        result = []
        for k, v in conditions.items():
            result.append({
                "name": "@%s" % k,
                "value": v
            })

        return result

    @staticmethod
    def check_visibility(item, throw_not_found_if_deleted):
        if throw_not_found_if_deleted and item.get('deleted') is not None:
            raise exceptions.CosmosResourceNotFoundError(message='Deleted item',
                                                         status_code=404)
        return item

    @staticmethod
    def replace_empty_value_per_none(item_data: dict) -> dict:
        for k, v in item_data.items():
            if isinstance(v, str) and len(v) == 0:
                item_data[k] = None

    @staticmethod
    def attach_context(data: dict, event_context: EventContext):
        data["_last_event_ctx"] = {
            "user_id": event_context.user_id,
            "tenant_id": event_context.tenant_id,
            "action": event_context.action,
            "description": event_context.description,
            "container_id": event_context.container_id,
            "session_id": event_context.session_id,
        }

    def create(self, data: dict, event_context: EventContext, mapper: Callable = None):
        self.on_create(data, event_context)
        function_mapper = self.get_mapper_or_dict(mapper)
        self.attach_context(data, event_context)
        return function_mapper(self.container.create_item(body=data))

    def find(self, id: str, event_context: EventContext, peeker: 'function' = None,
             visible_only=True, mapper: Callable = None):
        partition_key_value = self.find_partition_key_value(event_context)
        found_item = self.container.read_item(id, partition_key_value)
        if peeker:
            peeker(found_item)

        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(self.check_visibility(found_item, visible_only))

    def find_all(self, event_context: EventContext, conditions: dict = {}, max_count=None,
                 offset=0, visible_only=True, mapper: Callable = None):
        partition_key_value = self.find_partition_key_value(event_context)
        max_count = self.get_page_size_or(max_count)
        params = [
            {"name": "@partition_key_value", "value": partition_key_value},
            {"name": "@offset", "value": offset},
            {"name": "@max_count", "value": max_count},
        ]
        params.extend(self.generate_condition_values(conditions))
        result = self.container.query_items(query="""
            SELECT * FROM c WHERE c.{partition_key_attribute}=@partition_key_value
            {conditions_clause} {visibility_condition} {order_clause}
            OFFSET @offset LIMIT @max_count
            """.format(partition_key_attribute=self.partition_key_attribute,
                       visibility_condition=self.create_sql_condition_for_visibility(visible_only),
                       conditions_clause=self.create_sql_where_conditions(conditions),
                       order_clause=self.create_sql_order_clause()),
                                            parameters=params,
                                            partition_key=partition_key_value,
                                            max_item_count=max_count)

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def partial_update(self, id: str, changes: dict, event_context: EventContext,
                       peeker: 'function' = None, visible_only=True, mapper: Callable = None):
        item_data = self.find(id, event_context, peeker=peeker, visible_only=visible_only, mapper=dict)
        item_data.update(changes)
        return self.update(id, item_data, event_context, mapper=mapper)

    def update(self, id: str, item_data: dict, event_context: EventContext,
               mapper: Callable = None):
        self.on_update(item_data, event_context)
        function_mapper = self.get_mapper_or_dict(mapper)
        self.attach_context(item_data, event_context)
        return function_mapper(self.container.replace_item(id, body=item_data))

    def delete(self, id: str, event_context: EventContext,
               peeker: 'function' = None, mapper: Callable = None):
        return self.partial_update(id, {
            'deleted': generate_uuid4()
        }, event_context, peeker=peeker, visible_only=True, mapper=mapper)

    def delete_permanently(self, id: str, partition_key_value: str) -> None:
        self.container.delete_item(id, partition_key_value)

    def find_partition_key_value(self, event_context: EventContext):
        return getattr(event_context, self.partition_key_attribute)

    def get_mapper_or_dict(self, alternative_mapper: Callable) -> Callable:
        return alternative_mapper or self.mapper or dict

    def get_page_size_or(self, custom_page_size: int) -> int:
        # TODO The default value should be taken from the Azure Feature Manager
        # or any other repository for the settings
        return custom_page_size or 100

    def on_create(self, new_item_data: dict, event_context: EventContext):
        if new_item_data.get('id') is None:
            new_item_data['id'] = generate_uuid4()

        new_item_data[self.partition_key_attribute] = self.find_partition_key_value(event_context)

        self.replace_empty_value_per_none(new_item_data)

    def on_update(self, update_item_data: dict, event_context: EventContext):
        pass

    def create_sql_order_clause(self):
        if len(self.order_fields) > 0:
            return "ORDER BY c.{}".format(", c.".join(self.order_fields))
        return ""


class CosmosDBDao(CRUDDao):
    def __init__(self, repository: CosmosDBRepository):
        self.repository = repository

    def get_all(self, conditions: dict = {}) -> list:
        event_ctx = self.create_event_context("read-many")
        return self.repository.find_all(event_ctx, conditions=conditions)

    def get(self, id):
        event_ctx = self.create_event_context("read")
        return self.repository.find(id, event_ctx)

    def create(self, data: dict):
        event_ctx = self.create_event_context("create")
        return self.repository.create(data, event_ctx)

    def update(self, id, data: dict):
        event_ctx = self.create_event_context("update")
        return self.repository.partial_update(id, data, event_ctx)

    def delete(self, id):
        event_ctx = self.create_event_context("delete")
        self.repository.delete(id, event_ctx)

    @property
    def find_partition_key_value(self, event_context: EventContext):
        return event_context.tenant_id

    # Replace by decorator and put it in the repository
    def create_event_context(self, action: str = None, description: str = None):
        return EventContext(self.repository.container.id,
                            action,
                            description=description)


class CustomError(HTTPException):
    def __init__(self, status_code: int, description: str = None):
        self.code = status_code
        self.description = description


def current_datetime() -> datetime:
    return datetime.utcnow()


def datetime_str(value: datetime) -> str:
    if value is not None:
        return value.isoformat()
    else:
        return None


def current_datetime_str() -> str:
    return datetime_str(current_datetime())


def generate_uuid4() -> str:
    return str(uuid.uuid4())


def init_app(app: Flask) -> None:
    global cosmos_helper
    cosmos_helper = CosmosDBFacade.from_flask_config(app)
