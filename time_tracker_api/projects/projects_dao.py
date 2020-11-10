from azure.cosmos import PartitionKey
from commons.data_access_layer.cosmos_db import (
    CosmosDBDao,
    CosmosDBRepository,
)
from time_tracker_api.database import CRUDDao, APICosmosDBDao
from time_tracker_api.customers.customers_model import (
    create_dao as customers_create_dao,
)
from time_tracker_api.projects.projects_model import ProjectCosmosDBModel

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


class ProjectCosmosDBRepository(CosmosDBRepository):
    def __init__(self):
        CosmosDBRepository.__init__(
            self,
            container_id=container_definition['id'],
            partition_key_attribute='tenant_id',
            mapper=ProjectCosmosDBModel,
        )


class ProjectCosmosDBDao(APICosmosDBDao, ProjectDao):
    def __init__(self, repository):
        CosmosDBDao.__init__(self, repository)

    def get_all(self, conditions: dict = None, **kwargs) -> list:
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
