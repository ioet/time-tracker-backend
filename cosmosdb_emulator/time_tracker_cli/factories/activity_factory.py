from typing import NamedTuple

from factory import Factory, Faker

from cosmosdb_emulator.time_tracker_cli.providers.common import CommonProvider
from cosmosdb_emulator.time_tracker_cli.utils.common import (
    get_time_tracker_tenant_id,
)

Faker.add_provider(CommonProvider)


class Activity(NamedTuple):
    id: str
    name: str
    description: str
    status: str
    tenant_id: str


class ActivityFactory(Factory):
    class Meta:
        model = Activity

    id = Faker('uuid4')
    name = Faker('job')
    description = Faker('sentence', nb_words=6)
    status = Faker('status')
    tenant_id = get_time_tracker_tenant_id()
