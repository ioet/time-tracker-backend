from dataclasses import dataclass

from azure.cosmos import PartitionKey

from commons.data_access_layer.cosmos_db import CosmosDBModel, CosmosDBDao, CosmosDBRepository
from commons.data_access_layer.database import CRUDDao


class ProjectTypeDao(CRUDDao):
    pass


container_definition = {
    'id': 'project_type',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name', '/customer_id', '/deleted']},
        ]
    }
}


@dataclass()
class ProjectTypeCosmosDBModel(CosmosDBModel):
    id: str
    name: str
    description: str
    parent_id: str
    customer_id: str
    deleted: str
    tenant_id: str

    def __init__(self, data):
        super(ProjectTypeCosmosDBModel, self).__init__(data)  # pragma: no cover

    def __repr__(self):
        return '<ProjectType %r>' % self.name  # pragma: no cover

    def __str___(self):
        return "the project type \"%s\"" % self.name  # pragma: no cover


def create_dao() -> ProjectTypeDao:
    repository = CosmosDBRepository.from_definition(container_definition,
                                                    mapper=ProjectTypeCosmosDBModel)

    class ProjectTypeCosmosDBDao(CosmosDBDao, ProjectTypeDao):
        def __init__(self):
            CosmosDBDao.__init__(self, repository)

    return ProjectTypeCosmosDBDao()
