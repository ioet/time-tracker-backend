from dataclasses import dataclass

from azure.cosmos import PartitionKey

from commons.data_access_layer.cosmos_db import CosmosDBModel, CosmosDBDao, CosmosDBRepository
from commons.data_access_layer.database import CRUDDao

"""
Protocols
"""


class ProjectDao(CRUDDao):
    pass


"""
Cosmos DB
"""

container_definition = {
    'id': 'project',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name']},
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
        super(ProjectCosmosDBModel, self).__init__(data)

    def __repr__(self):
        return '<Project %r>' % self.name

    def __str___(self):
        return "the project \"%s\"" % self.name


def create_dao() -> ProjectDao:
    repository = CosmosDBRepository.from_definition(container_definition,
                                                    mapper=ProjectCosmosDBModel)

    class ProjectCosmosDBDao(CosmosDBDao, ProjectDao):
        def __init__(self):
            CosmosDBDao.__init__(self, repository)

    return ProjectCosmosDBDao()
