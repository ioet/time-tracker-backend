from typing import List

from cosmosdb_emulator.time_tracker_cli.factories.activity_factory import (
    ActivityFactory,
)


def get_activity_json(activity_factory: ActivityFactory) -> dict:
    activity = {
        'id': activity_factory.id,
        'name': activity_factory.name,
        'description': activity_factory.description,
        'tenant_id': activity_factory.tenant_id,
        'status': activity_factory.status,
    }

    return activity


def get_activities(activities_amount: int) -> List[ActivityFactory]:
    activities = []
    for index in range(activities_amount):
        activity = ActivityFactory()
        activities.append(activity)
    return activities
