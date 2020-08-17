from dataclasses import dataclass

from azure.cosmos import PartitionKey

from commons.data_access_layer.cosmos_db import (
    CosmosDBModel,
    CosmosDBDao,
    CosmosDBRepository,
)
from time_tracker_api.database import CRUDDao, APICosmosDBDao


class TechnologyDao(CRUDDao):
    pass


container_definition = {
    'id': 'technology',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {'uniqueKeys': [{'paths': ['/name']},]},
}


@dataclass()
class TechnologyCosmosDBModel(CosmosDBModel):
    id: str
    name: str
    first_use_time_entry_id: str
    creation_date: str
    deleted: str
    tenant_id: str

    def __init__(self, data):
        super(TechnologyCosmosDBModel, self).__init__(data)  # pragma: no cover

    def __repr__(self):
        return '<Technology %r>' % self.name  # pragma: no cover

    def __str___(self):
        return "the Technology \"%s\"" % self.name  # pragma: no cover


def create_dao() -> TechnologyDao:
    repository = CosmosDBRepository.from_definition(
        container_definition, mapper=TechnologyCosmosDBModel
    )

    class TechnologyCosmosDBDao(APICosmosDBDao, TechnologyDao):
        def __init__(self):
            CosmosDBDao.__init__(self, repository)

    return TechnologyCosmosDBDao()
