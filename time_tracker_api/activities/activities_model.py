from dataclasses import dataclass

from azure.cosmos import PartitionKey

from commons.data_access_layer.cosmos_db import CosmosDBModel, CosmosDBDao, CosmosDBRepository
from commons.data_access_layer.database import CRUDDao


class ActivityDao(CRUDDao):
    pass


container_definition = {
    'id': 'activity',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name']},
        ]
    }
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


def create_dao() -> ActivityDao:
    repository = CosmosDBRepository.from_definition(container_definition,
                                                    mapper=ActivityCosmosDBModel)

    class ActivityCosmosDBDao(CosmosDBDao, ActivityDao):
        def __init__(self):
            CosmosDBDao.__init__(self, repository)

    return ActivityCosmosDBDao()
