from dataclasses import dataclass

from azure.cosmos import PartitionKey

from commons.data_access_layer.cosmos_db import (
    CosmosDBModel,
    CosmosDBDao,
    CosmosDBRepository,
)
from time_tracker_api.database import CRUDDao, APICosmosDBDao
from typing import List, Callable
from commons.data_access_layer.database import EventContext
from utils.enums.status import Status
from utils.query_builder import CosmosDBQueryBuilder
from commons.data_access_layer.file_stream import FileStream

class ActivityDao(CRUDDao):
    pass


container_definition = {
    'id': 'activity',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name', '/deleted']},
        ]
    },
}


@dataclass()
class ActivityCosmosDBModel(CosmosDBModel):
    id: str
    name: str
    description: str
    deleted: str
    status: str
    tenant_id: str

    def __init__(self, data):
        super(ActivityCosmosDBModel, self).__init__(data)  # pragma: no cover

    def __repr__(self):
        return '<Activity %r>' % self.name  # pragma: no cover

    def __str___(self):
        return "the activity \"%s\"" % self.name  # pragma: no cover


class ActivityCosmosDBRepository(CosmosDBRepository):
    def __init__(self):
        CosmosDBRepository.__init__(
            self,
            container_id=container_definition['id'],
            partition_key_attribute='tenant_id',
            mapper=ActivityCosmosDBModel,
        )

    def find_all_with_id_in_list(
        self,
        event_context: EventContext,
        activity_ids: List[str],
        visible_only=True,
        mapper: Callable = None,
    ):
        query_builder = (
            CosmosDBQueryBuilder()
            .add_sql_in_condition('id', activity_ids)
            .add_sql_visibility_condition(visible_only)
            .build()
        )
        query_str = query_builder.get_query()

        tenant_id_value = self.find_partition_key_value(event_context)
        result = self.container.query_items(
            query=query_str,
            partition_key=tenant_id_value,
        )

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def find_all(
        self,
        event_context: EventContext,
        conditions: dict = None,
        activities_id: List = None,
        visible_only=True,
        max_count=None,
        offset=0,
        mapper: Callable = None,
    ):
        query_builder = (
            CosmosDBQueryBuilder()
            .add_sql_in_condition('id', activities_id)
            .add_sql_where_equal_condition(conditions)
            .add_sql_visibility_condition(visible_only)
            .add_sql_limit_condition(max_count)
            .add_sql_offset_condition(offset)
            .build()
        )

        query_str = query_builder.get_query()
        tenant_id_value = self.find_partition_key_value(event_context)
        params = query_builder.get_parameters()

        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=tenant_id_value,
        )
        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def find_all_from_blob_storage(self, event_context: EventContext, mapper: Callable = None):
        tenant_id_value = self.find_partition_key_value(event_context)
        function_mapper = self.get_mapper_or_dict(mapper)
        if tenant_id_value is None:
            return []
            
        import json
        fs = FileStream("storageaccounteystr82c5","tt-common-files")
        result = fs.get_file_stream("activity.json")
        return list(map(function_mapper, json.load(result))) if result is not None else []

class ActivityCosmosDBDao(APICosmosDBDao, ActivityDao):
    def __init__(self, repository):
        CosmosDBDao.__init__(self, repository)

    def get_all_with_id_in_list(
        self,
        activity_ids,
    ):
        event_ctx = self.create_event_context("read-many")
        return self.repository.find_all_with_id_in_list(
            event_ctx,
            activity_ids,
        )

    def get_all_old(
        self,
        conditions: dict = None,
        activities_id: List = None,
        max_count=None,
        visible_only=True,
    ) -> list:
        event_ctx = self.create_event_context("read-many")
        max_count = self.repository.get_page_size_or(max_count)

        activities = self.repository.find_all(
            event_context=event_ctx,
            conditions=conditions,
            activities_id=activities_id,
            visible_only=visible_only,
            max_count=max_count,
        )
        return activities

    def get_all(self, conditions: dict = None) -> list:
            event_ctx = self.create_event_context("read-many")
            activities = self.repository.find_all_from_blob_storage(event_context=event_ctx)
            return activities

    def create(self, activity_payload: dict):
        event_ctx = self.create_event_context('create')
        activity_payload['status'] = Status.ACTIVE.value
        return self.repository.create(
            data=activity_payload, event_context=event_ctx
        )


def create_dao() -> ActivityDao:
    repository = ActivityCosmosDBRepository()

    return ActivityCosmosDBDao(repository)
