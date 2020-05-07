from dataclasses import dataclass
from azure.cosmos import PartitionKey
from commons.data_access_layer.cosmos_db import CosmosDBModel, CosmosDBDao, CosmosDBRepository
from time_tracker_api.database import CRUDDao, APICosmosDBDao
from time_tracker_api.customers.customers_model import create_dao as customers_create_dao


class ProjectDao(CRUDDao):
    pass


container_definition = {
    'id': 'project',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name', '/customer_id', '/deleted']},
        ]
    }
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

    def __init__(self, data):
        super(ProjectCosmosDBModel, self).__init__(data)  # pragma: no cover 

    def __repr__(self):
        return '<Project %r>' % self.name  # pragma: no cover

    def __str___(self):
        return "the project \"%s\"" % self.name  # pragma: no cover


class ProjectCosmosDBRepository(CosmosDBRepository):
    def __init__(self):
        CosmosDBRepository.__init__(self, container_id=container_definition['id'],
                                    partition_key_attribute='tenant_id',
                                    mapper=ProjectCosmosDBModel)


class ProjectCosmosDBDao(APICosmosDBDao, ProjectDao):
    def __init__(self, repository):
        CosmosDBDao.__init__(self, repository)

    def get_all(self, conditions: dict = None, **kwargs) -> list:
        event_ctx = self.create_event_context("read-many")
        customer_dao = customers_create_dao()
        customers = customer_dao.get_all(visible_only=False)
        projects = self.repository.find_all(event_ctx, **kwargs)
        for project in projects:
            print(project.__dict__)

        return projects


def create_dao() -> ProjectDao:
    repository = ProjectCosmosDBRepository()

    return ProjectCosmosDBDao(repository)
