from typing import NamedTuple

from factory import Factory, Faker

from cosmosdb_emulator.time_tracker_cli.utils.common import (
    get_time_tracker_tenant_id,
)


class Customer(NamedTuple):
    id: str
    name: str
    description: str
    tenant_id: str


class CustomerFactory(Factory):
    class Meta:
        model = Customer

    id = Faker('uuid4')
    name = Faker('company')
    description = Faker('sentence', nb_words=10)
    tenant_id = get_time_tracker_tenant_id()
