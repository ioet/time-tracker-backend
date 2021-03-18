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
from utils.repository import convert_list_to_tuple_string


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

    def create_sql_in_condition(self, activity_ids):
        id_values = convert_list_to_tuple_string(activity_ids)

        return "c.id IN {value_condition}".format(value_condition=id_values)

    def find_all_with_id_in_list(
        self,
        event_context: EventContext,
        activity_ids: List[str],
        visible_only=True,
        mapper: Callable = None,
    ):
        visibility = self.create_sql_condition_for_visibility(visible_only)
        query_str = """
            SELECT * FROM c
            WHERE {condition}
            {visibility_condition}
            """.format(
            condition=self.create_sql_in_condition(activity_ids),
            visibility_condition=visibility,
        )

        tenant_id_value = self.find_partition_key_value(event_context)
        result = self.container.query_items(
            query=query_str,
            partition_key=tenant_id_value,
        )

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))


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


def create_dao() -> ActivityDao:
    repository = ActivityCosmosDBRepository()

    return ActivityCosmosDBDao(repository)
