from dataclasses import dataclass

from azure.cosmos import PartitionKey

from commons.data_access_layer.cosmos_db import CosmosDBModel, CosmosDBRepository, CosmosDBDao
from commons.data_access_layer.database import CRUDDao


class CustomerDao(CRUDDao):
    pass


container_definition = {
    'id': 'customer',
    'partition_key': PartitionKey(path='/tenant_id'),
    'unique_key_policy': {
        'uniqueKeys': [
            {'paths': ['/name']},
        ]
    }
}


@dataclass()
class CustomerCosmosDBModel(CosmosDBModel):
    id: str
    name: str
    description: str
    deleted: str
    tenant_id: str

    def __init__(self, data):
        super(CustomerCosmosDBModel, self).__init__(data)  # pragma: no cover

    def __repr__(self):
        return '<Customer %r>' % self.name  # pragma: no cover

    def __str___(self):
        return "the customer \"%s\"" % self.name  # pragma: no cover


def create_dao() -> CustomerDao:
    repository = CosmosDBRepository.from_definition(container_definition,
                                                    mapper=CustomerCosmosDBModel)

    class CustomerCosmosDBDao(CosmosDBDao, CustomerDao):
        def __init__(self):
            CosmosDBDao.__init__(self, repository)

    return CustomerCosmosDBDao()