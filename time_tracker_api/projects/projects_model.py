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
from time_tracker_api.customers.customers_model import (
    create_dao as customers_create_dao,
)
from time_tracker_api.customers.customers_model import CustomerCosmosDBModel

from utils.extend_model import add_customer_name_to_projects


class ProjectDao(CRUDDao):
    pass


container_definition = {
    'id': 'project',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [{'paths': ['/name', '/customer_id', '/deleted']},]
    },
}


@dataclass()
class ProjectCosmosDBModel(CosmosDBModel):
    id: str
    name: str
    description: str
    project_type_id: int
    customer_id: str
    deleted: str
    tenant_id: str
    technologies: list

    def __init__(self, data):
        super(ProjectCosmosDBModel, self).__init__(data)  # pragma: no cover

    def __contains__(self, item):
        if type(item) is CustomerCosmosDBModel:
            return True if item.id == self.customer_id else False
        else:
            raise NotImplementedError

    def __repr__(self):
        return '<Project %r>' % self.name  # pragma: no cover

    def __str___(self):
        return "the project \"%s\"" % self.name  # pragma: no cover


class ProjectCosmosDBRepository(CosmosDBRepository):
    def __init__(self):
        CosmosDBRepository.__init__(
            self,
            container_id=container_definition['id'],
            partition_key_attribute='tenant_id',
            mapper=ProjectCosmosDBModel,
        )

    def create_sql_in_condition(self, customer_ids_list):
        id_values = convert_list_to_tuple_string(customer_ids_list)

        return "c.customer_id IN {value_condition}".format(value_condition=id_values)
    
    def find_all_with_customer_id_in_list(
        self,
        event_context: EventContext,
        customer_ids_list: List[str],
        visible_only=True,
        mapper: Callable = None,
    ):  
        visibility = self.create_sql_condition_for_visibility(visible_only)
        query_str = """
            SELECT * FROM c
            WHERE {condition}
            {visibility_condition}
            """.format(
            condition=self.create_sql_in_condition(customer_ids_list),
            visibility_condition=visibility,
        )
        
        tenant_id_value = self.find_partition_key_value(event_context)
        result = self.container.query_items(
            query=query_str,
            partition_key=tenant_id_value,
        )
        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))


class ProjectCosmosDBDao(APICosmosDBDao, ProjectDao):
    def __init__(self, repository):
        CosmosDBDao.__init__(self, repository)

    def get_all(self, conditions: dict = None, **kwargs) -> list:
        """
        Get all the projects an active client has
        :param (dict) conditions: Conditions for querying the database
        :param (dict) kwargs: Pass arguments
        :return (list): ProjectCosmosDBModel object list
        """
        event_ctx = self.create_event_context("read-many")
        customer_dao = customers_create_dao()
        customers = customer_dao.get_all(
            max_count=kwargs.get('max_count', None)
        )

        customers_id = [customer.id for customer in customers]
        conditions = conditions if conditions else {}
        custom_condition = "c.customer_id IN {}".format(
            str(tuple(customers_id))
        )
        # TODO this must be refactored to be used from the utils module ↑
        if "custom_sql_conditions" in kwargs:
            kwargs["custom_sql_conditions"].append(custom_condition)
        else:
            kwargs["custom_sql_conditions"] = [custom_condition]
        projects = self.repository.find_all(event_ctx, conditions, **kwargs)

        add_customer_name_to_projects(projects, customers)
        return projects


def create_dao() -> ProjectDao:
    repository = ProjectCosmosDBRepository()

    return ProjectCosmosDBDao(repository)
