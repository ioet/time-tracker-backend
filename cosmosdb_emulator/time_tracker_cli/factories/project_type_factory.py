from typing import NamedTuple

from factory import Factory, Faker

from cosmosdb_emulator.time_tracker_cli.utils.common import (
    get_time_tracker_tenant_id,
)


class ProjectType(NamedTuple):
    id: str
    name: str
    description: str
    customer_id: str
    tenant_id: str


class ProjectTypeFactory(Factory):
    class Meta:
        model = ProjectType

    def __init__(self, customer_id):
        self.customer_id = customer_id

    id = Faker('uuid4')
    name = Faker('name')
    description = Faker('sentence', nb_words=10)
    tenant_id = get_time_tracker_tenant_id()
