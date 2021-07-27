import dataclasses
import logging
from typing import Callable

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import ContainerProxy, PartitionKey
from flask import Flask
from werkzeug.exceptions import HTTPException

from commons.data_access_layer.database import CRUDDao, EventContext
from utils.query_builder import CosmosDBQueryBuilder


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
            app.logger.warn(
                "COSMOS_DATABASE_URI was not found. Looking for alternative variables."
            )
            account_uri = app.config.get('DATABASE_ACCOUNT_URI')
            if account_uri is None:
                raise EnvironmentError(
                    "DATABASE_ACCOUNT_URI is not defined in the environment"
                )

            master_key = app.config.get('DATABASE_MASTER_KEY')
            if master_key is None:
                raise EnvironmentError(
                    "DATABASE_MASTER_KEY is not defined in the environment"
                )

            client = cosmos_client.CosmosClient(
                account_uri,
                {'masterKey': master_key},
                user_agent="TimeTrackerAPI",
                user_agent_overwrite=True,
            )
        else:
            client = cosmos_client.CosmosClient.from_connection_string(db_uri)

        db_id = app.config.get('DATABASE_NAME')
        if db_id is None:
            raise EnvironmentError(
                "DATABASE_NAME is not defined in the environment"
            )

        return cls(client, db_id, logger=app.logger)

    def create_container(self, container_definition: dict):
        return self.db.create_container(**container_definition)

    def create_container_if_not_exists(self, container_definition: dict):
        return self.db.create_container_if_not_exists(**container_definition)

    def delete_container(self, container_id: str):
        return self.db.delete_container(container_id)


cosmos_helper: CosmosDBFacade = None


class CosmosDBModel:
    def __init__(self, data):
        names = set([f.name for f in dataclasses.fields(self)])
        for k, v in data.items():
            if k in names:
                setattr(self, k, v)

    def is_deleted(self):
        if "deleted" in self.__dict__.keys():
            return True if self.deleted else False
        return False


def partition_key_attribute(pk: PartitionKey) -> str:
    return pk.path.strip('/')


class CosmosDBRepository:
    def __init__(
        self,
        container_id: str,
        partition_key_attribute: str,
        mapper: Callable = None,
        order_fields: list = None,
        custom_cosmos_helper: CosmosDBFacade = None,
    ):
        global cosmos_helper
        self.cosmos_helper = custom_cosmos_helper or cosmos_helper
        if self.cosmos_helper is None:  # pragma: no cover
            raise ValueError("The cosmos_db module has not been initialized!")
        self.mapper = mapper
        self.order_fields = order_fields if order_fields else []
        self.container: ContainerProxy = (
            self.cosmos_helper.db.get_container_client(container_id)
        )
        self.partition_key_attribute = partition_key_attribute

    @classmethod
    def from_definition(
        cls,
        container_definition: dict,
        mapper: Callable = None,
        custom_cosmos_helper: CosmosDBFacade = None,
    ):
        pk_attrib = partition_key_attribute(
            container_definition['partition_key']
        )
        return cls(
            container_definition['id'],
            pk_attrib,
            mapper=mapper,
            custom_cosmos_helper=custom_cosmos_helper,
        )

    @staticmethod
    def create_sql_condition_for_visibility(
        visible_only: bool, container_name='c'
    ) -> str:
        if visible_only:
            # We are considering that `deleted == null` is not a choice
            return 'AND NOT IS_DEFINED(%s.deleted)' % container_name
        return ''

    @staticmethod
    def create_sql_active_condition(
        status_value: str, container_name='c'
    ) -> str:
        if status_value != None:
            not_defined_condition = ''
            condition_operand = ' AND '
            if status_value == 'active':
                not_defined_condition = (
                    'AND NOT IS_DEFINED({container_name}.status)'.format(
                        container_name=container_name
                    )
                )
                condition_operand = ' OR '

            defined_condition = '(IS_DEFINED({container_name}.status) \
                AND {container_name}.status = \'{status_value}\')'.format(
                container_name=container_name, status_value=status_value
            )
            return (
                not_defined_condition + condition_operand + defined_condition
            )

        return ''

    @staticmethod
    def create_sql_where_conditions(
        conditions: dict, container_name='c'
    ) -> str:
        where_conditions = []
        for k in conditions.keys():
            where_conditions.append(f'{container_name}.{k} = @{k}')

        if len(where_conditions) > 0:
            return "AND {where_conditions_clause}".format(
                where_conditions_clause=" AND ".join(where_conditions)
            )
        else:
            return ""

    @staticmethod
    def generate_params(conditions: dict) -> list:
        result = []
        for k, v in conditions.items():
            result.append({"name": "@%s" % k, "value": v})

        return result

    @staticmethod
    def check_visibility(item, throw_not_found_if_deleted):
        if throw_not_found_if_deleted and item.get('deleted') is not None:
            raise exceptions.CosmosResourceNotFoundError(
                message='Deleted item', status_code=404
            )
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

    @staticmethod
    def create_sql_date_range_filter(date_range: dict) -> str:
        if 'start_date' in date_range and 'end_date' in date_range:
            return """
                AND ((c.start_date BETWEEN @start_date AND @end_date) OR
                 (c.end_date BETWEEN @start_date AND @end_date))
                """
        else:
            return ''

    def create(
        self, data: dict, event_context: EventContext, mapper: Callable = None
    ):
        self.on_create(data, event_context)
        function_mapper = self.get_mapper_or_dict(mapper)
        self.attach_context(data, event_context)
        return function_mapper(self.container.create_item(body=data))

    def on_create(self, new_item_data: dict, event_context: EventContext):
        if new_item_data.get('id') is None:
            new_item_data['id'] = generate_uuid4()

        new_item_data[
            self.partition_key_attribute
        ] = self.find_partition_key_value(event_context)

        self.replace_empty_value_per_none(new_item_data)

    def find(
        self,
        id: str,
        event_context: EventContext,
        visible_only=True,
        mapper: Callable = None,
    ):
        partition_key_value = self.find_partition_key_value(event_context)
        found_item = self.container.read_item(id, partition_key_value)
        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(self.check_visibility(found_item, visible_only))

    def find_all(
        self,
        event_context: EventContext,
        conditions: dict = None,
        date_range: dict = None,
        visible_only=True,
        max_count=None,
        offset=0,
        mapper: Callable = None,
    ):
        conditions = conditions if conditions else {}
        max_count: int = self.get_page_size_or(max_count)

        status_value = conditions.get('status')
        if status_value:
            conditions.pop('status')

        date_range = date_range if date_range else {}

        query_builder = (
            CosmosDBQueryBuilder()
            .add_sql_where_equal_condition(conditions)
            .add_sql_active_condition(status_value)
            .add_sql_date_range_filter(date_range)
            .add_sql_visibility_condition(visible_only)
            .add_sql_limit_condition(max_count)
            .add_sql_offset_condition(offset)
            .build()
        )

        if len(self.order_fields) > 1:
            attribute = self.order_fields[0]
            order = self.order_fields[1]
            query_builder.add_sql_order_by_condition(attribute, order)

        query_str = query_builder.get_query()
        params = query_builder.get_parameters()
        partition_key_value = self.find_partition_key_value(event_context)

        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=partition_key_value,
        )

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def partial_update(
        self,
        id: str,
        changes: dict,
        event_context: EventContext,
        visible_only=True,
        mapper: Callable = None,
    ):
        item_data = self.find(
            id,
            event_context,
            visible_only=visible_only,
            mapper=dict,
        )
        item_data.update(changes)
        return self.update(id, item_data, event_context, mapper=mapper)

    def update(
        self,
        id: str,
        item_data: dict,
        event_context: EventContext,
        mapper: Callable = None,
    ):
        self.on_update(item_data, event_context)
        function_mapper = self.get_mapper_or_dict(mapper)
        self.attach_context(item_data, event_context)
        return function_mapper(self.container.replace_item(id, body=item_data))

    def delete(
        self,
        id: str,
        event_context: EventContext,
        mapper: Callable = None,
    ):
        return self.partial_update(
            id,
            {'deleted': generate_uuid4()},
            event_context,
            visible_only=True,
            mapper=mapper,
        )

    def delete_permanently(self, id: str, event_context: EventContext) -> None:
        partition_key_value = self.find_partition_key_value(event_context)
        self.container.delete_item(id, partition_key_value)

    def find_partition_key_value(self, event_context: EventContext):
        return getattr(event_context, self.partition_key_attribute)

    def get_mapper_or_dict(self, alternative_mapper: Callable) -> Callable:
        return alternative_mapper or self.mapper or dict

    def get_page_size_or(self, custom_page_size: int) -> int:
        # TODO The default value should be taken from the Azure Feature Manager
        # or any other repository for the settings
        return custom_page_size or 9999

    def on_update(self, update_item_data: dict, event_context: EventContext):
        pass

    def create_sql_order_clause(self):
        if len(self.order_fields) > 0:
            return "ORDER BY c.{}".format(", c.".join(self.order_fields))
        return ""


class CosmosDBDao(CRUDDao):
    def __init__(self, repository: CosmosDBRepository):
        self.repository = repository

    def get_all(self, conditions: dict = None, **kwargs) -> list:
        conditions = conditions if conditions else {}
        event_ctx = self.create_event_context("read-many")
        return self.repository.find_all(
            event_ctx, conditions=conditions, **kwargs
        )

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

    def create_event_context(
        self, action: str = None, description: str = None
    ):
        return EventContext(
            self.repository.container.id, action, description=description
        )


class CustomError(HTTPException):
    def __init__(self, status_code: int, description: str = None):
        self.code = status_code
        self.description = description


def init_app(app: Flask) -> None:
    global cosmos_helper
    cosmos_helper = CosmosDBFacade.from_flask_config(app)


def generate_uuid4() -> str:
    from uuid import uuid4

    return str(uuid4())
