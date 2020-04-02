import dataclasses
import uuid
from typing import Callable

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import ContainerProxy
from flask import Flask


class CosmosDBFacade:
    def __init__(self, app: Flask):  # pragma: no cover
        self.app = app

        db_uri = app.config.get('DATABASE_URI')
        if db_uri is None:
            app.logger.warn("DATABASE_URI was not found. Looking for alternative variables.")
            account_uri = app.config.get('DATABASE_ACCOUNT_URI')
            if account_uri is None:
                raise EnvironmentError("DATABASE_ACCOUNT_URI is not defined in the environment")

            master_key = app.config.get('DATABASE_MASTER_KEY')
            if master_key is None:
                raise EnvironmentError("DATABASE_MASTER_KEY is not defined in the environment")

            self.client = cosmos_client.CosmosClient(account_uri, {'masterKey': master_key},
                                                     user_agent="CosmosDBDotnetQuickstart",
                                                     user_agent_overwrite=True)
        else:
            self.client = cosmos_client.CosmosClient.from_connection_string(db_uri)

        db_id = app.config.get('DATABASE_NAME')
        if db_id is None:
            raise EnvironmentError("DATABASE_NAME is not defined in the environment")

        self.db = self.client.get_database_client(db_id)

    def create_container(self, container_definition: dict):
        try:
            return self.db.create_container(**container_definition)

        except exceptions.CosmosResourceExistsError:  # pragma: no cover
            self.app.logger.info('Container with id \'{0}\' was found'.format(container_definition["id"]))

    def delete_container(self, container_id: str):
        try:
            return self.db.delete_container(container_id)

        except exceptions.CosmosHttpResponseError:  # pragma: no cover
            self.app.logger.info('Container with id \'{0}\' was not deleted'.format(container_id))


cosmos_helper: CosmosDBFacade = None


class CosmosDBModel():
    def __init__(self, data):
        names = set([f.name for f in dataclasses.fields(self)])
        for k, v in data.items():
            if k in names:
                setattr(self, k, v)


class CosmosDBRepository:
    def __init__(self, container_id: str,
                 mapper: Callable = None,
                 custom_cosmos_helper: CosmosDBFacade = None):
        global cosmos_helper
        self.cosmos_helper = custom_cosmos_helper or cosmos_helper
        if self.cosmos_helper is None:  # pragma: no cover
            raise ValueError("The cosmos_db module has not been initialized!")
        self.mapper = mapper
        self.container: ContainerProxy = self.cosmos_helper.db.get_container_client(container_id)

    @classmethod
    def from_definition(cls, container_definition: dict,
                        mapper: Callable = None,
                        custom_cosmos_helper: CosmosDBFacade = None):
        return cls(container_definition['id'], mapper, custom_cosmos_helper)

    def create(self, data: dict, mapper: Callable = None):
        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(self.container.create_item(body=data))

    def find(self, id: str, partition_key_value, visible_only=True, mapper: Callable = None):
        found_item = self.container.read_item(id, partition_key_value)
        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(self.check_visibility(found_item, visible_only))

    def find_all(self, partition_key_value: str, max_count=None, offset=0,
                 visible_only=True, mapper: Callable = None):
        # TODO Use the tenant_id param and change container alias
        max_count = self.get_page_size_or(max_count)
        result = self.container.query_items(
            query="""
            SELECT * FROM c WHERE c.tenant_id=@tenant_id AND {visibility_condition}
            OFFSET @offset LIMIT @max_count
            """.format(visibility_condition=self.create_sql_condition_for_visibility(visible_only)),
            parameters=[
                {"name": "@tenant_id", "value": partition_key_value},
                {"name": "@offset", "value": offset},
                {"name": "@max_count", "value": max_count},
            ],
            partition_key=partition_key_value,
            max_item_count=max_count)

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def partial_update(self, id: str, changes: dict, partition_key_value: str,
                       visible_only=True, mapper: Callable = None):
        item_data = self.find(id, partition_key_value, visible_only=visible_only)
        item_data.update(changes)
        return self.update(id, item_data, mapper=mapper)

    def update(self, id: str, item_data: dict, mapper: Callable = None):
        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(self.container.replace_item(id, body=item_data))

    def delete(self, id: str, partition_key_value: str, mapper: Callable = None):
        return self.partial_update(id, {
            'deleted': str(uuid.uuid4())
        }, partition_key_value, visible_only=True, mapper=mapper)

    def check_visibility(self, item, throw_not_found_if_deleted):
        if throw_not_found_if_deleted and item.get('deleted') is not None:
            raise exceptions.CosmosResourceNotFoundError(message='Deleted item',
                                                         status_code=404)

        return item

    def create_sql_condition_for_visibility(self, visible_only: bool, container_name='c') -> str:
        if visible_only:
            # We are considering that `deleted == null` is not a choice
            return 'NOT IS_DEFINED(%s.deleted)' % container_name
        return 'true'

    def get_mapper_or_dict(self, alternative_mapper: Callable) -> Callable:
        return alternative_mapper or self.mapper or dict

    def get_page_size_or(self, custom_page_size: int) -> int:
        # TODO The default value should be taken from the Azure Feature Manager
        # or any other repository for the settings
        return custom_page_size or 100


def init_app(app: Flask) -> None:
    global cosmos_helper
    cosmos_helper = CosmosDBFacade(app)
