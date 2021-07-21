from typing import NamedTuple

from factory import Factory, Faker

from cosmosdb_emulator.time_tracker_cli.utils.common import (
    get_time_tracker_tenant_id,
)


class Project(NamedTuple):
    id: str
    name: str
    description: str
    project_type_id: int
    customer_id: str
    tenant_id: str


class ProjectFactory(Factory):
    class Meta:
        model = Project

    def __init__(self, project_type_id, customer_id):
        self.project_type_id = project_type_id
        self.customer_id = customer_id

    id = Faker('uuid4')
    name = Faker('name')
    description = Faker('sentence', nb_words=10)
    tenant_id = get_time_tracker_tenant_id()
