from dataclasses import dataclass
from commons.data_access_layer.cosmos_db import (
    CosmosDBModel,
)
from time_tracker_api.customers.customers_model import CustomerCosmosDBModel


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
