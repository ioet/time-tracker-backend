from typing import NamedTuple, List

from factory import Factory, Faker

from cosmosdb_emulator.time_tracker_cli.utils.common import (
    get_time_tracker_tenant_id,
)


class TimeEntry(NamedTuple):
    project_id: str
    start_date: str
    owner_id: str
    id: str
    tenant_id: str
    description: str
    activity_id: str
    technologies: List[str]
    end_date: str


class TimeEntryFactory(Factory):
    class Meta:
        model = TimeEntry

    def __init__(
        self, owner_id, start_date, end_date, project_id, activity_id
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.owner_id = owner_id
        self.project_id = project_id
        self.activity_id = activity_id

    id = Faker('uuid4')
    description = Faker('sentence', nb_words=10)
    technologies = Faker('words', nb=3)
    tenant_id = get_time_tracker_tenant_id()
