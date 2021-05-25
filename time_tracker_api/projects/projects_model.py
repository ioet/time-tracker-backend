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
from time_tracker_api.customers.customers_model import (
    create_dao as customers_create_dao,
)
from time_tracker_api.project_types.project_types_model import (
    create_dao as project_types_create_dao,
)
from time_tracker_api.customers.customers_model import CustomerCosmosDBModel
from utils.query_builder import CosmosDBQueryBuilder
from utils.extend_model import (
    add_customer_name_to_projects,
    add_custom_attribute_in_list,
    add_custom_attribute
)


class ProjectDao(CRUDDao):
    pass


container_definition = {
    'id': 'project',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name', '/customer_id', '/deleted']},
        ]
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
    status: str
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

    def find_all(
        self,
        event_context: EventContext,
        conditions: dict = None,
        project_ids: List[str] = None,
        customer_ids: List[str] = None,
        visible_only=True,
        mapper: Callable = None,
    ):
        query_builder = (
            CosmosDBQueryBuilder()
            .add_sql_where_equal_condition(conditions)
            .add_sql_in_condition("id", project_ids)
            .add_sql_in_condition("customer_id", customer_ids)
            .add_sql_visibility_condition(visible_only)
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


class ProjectCosmosDBDao(APICosmosDBDao, ProjectDao):
    def __init__(self, repository):
        CosmosDBDao.__init__(self, repository)

    @add_custom_attribute('customer', customers_create_dao())
    @add_custom_attribute('project_type', project_types_create_dao())
    def get(self, id) -> ProjectCosmosDBModel:
        """
        Get one project an active client
        :param (str) id: project's id
        """
        return super().get(id)

    @add_custom_attribute_in_list('customer', customers_create_dao())
    @add_custom_attribute_in_list('project_type', project_types_create_dao())
    def get_all(self, conditions: dict = None, project_ids: List = None, **kwargs) -> list:
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

        customers_id = [
            customer.id
            for customer in customers
            if customer.status == 'active'
        ]

        conditions = conditions if conditions else {}

        projects = self.repository.find_all(
            event_context=event_ctx,
            conditions=conditions,
            project_ids=project_ids,
            customer_ids=customers_id,
        )

        add_customer_name_to_projects(projects, customers)
        return projects


def create_dao() -> ProjectDao:
    repository = ProjectCosmosDBRepository()

    return ProjectCosmosDBDao(repository)
