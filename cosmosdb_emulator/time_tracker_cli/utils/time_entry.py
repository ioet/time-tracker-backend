import math
from datetime import datetime, timedelta
from typing import List

from cosmosdb_emulator.time_tracker_cli.enums.entites import (
    TimeTrackerEntities,
)
from cosmosdb_emulator.time_tracker_cli.factories.activity_factory import (
    ActivityFactory,
)
from cosmosdb_emulator.time_tracker_cli.factories.project_factory import (
    ProjectFactory,
)
from cosmosdb_emulator.time_tracker_cli.factories.time_entry_factory import (
    TimeEntryFactory,
)
from cosmosdb_emulator.time_tracker_cli.utils.activity import get_activities
from cosmosdb_emulator.time_tracker_cli.utils.common import (
    get_random_element_from_list,
)
from cosmosdb_emulator.time_tracker_cli.utils.customer import get_customers
from cosmosdb_emulator.time_tracker_cli.utils.project import get_projects
from cosmosdb_emulator.time_tracker_cli.utils.project_type import (
    get_project_types,
)
from utils.azure_users import AzureConnection

"""
Note that the time zone in the DB is different from how it is handled in the UI.
For example 13:00 in the DB in the UI it will be 08:00
"""
base_hour = 13
base_minute = 0


def get_time_tracker_users_ids() -> List[str]:
    time_tracker_users = AzureConnection().users()
    users_ids = [user.id for user in time_tracker_users]
    return users_ids


def get_reference_datetime(
    entries_amount: int, daily_entries_amount: int
) -> datetime:
    amount_of_days = math.ceil(entries_amount / daily_entries_amount)
    base_datetime = datetime.today() - timedelta(days=amount_of_days)
    base_datetime = base_datetime.replace(hour=base_hour, minute=base_minute)
    return base_datetime


def get_next_day_from_datetime(reference_date: datetime) -> datetime:
    next_day = reference_date + timedelta(days=1)
    next_day = next_day.replace(hour=base_hour, minute=base_minute)
    return next_day


def get_time_entry_duration() -> int:
    time_entries_duration = [30, 40, 50, 60, 70, 80, 90, 100, 120]
    time_entry_duration = get_random_element_from_list(time_entries_duration)
    return time_entry_duration


def get_time_entry_end_date(entry_start_date) -> datetime:
    entry_duration = get_time_entry_duration()
    entry_end_date = entry_start_date + timedelta(minutes=entry_duration)
    return entry_end_date


def get_related_information_for_entries() -> dict:
    customers = get_customers(customer_amount=10)
    project_types = get_project_types(
        project_types_per_customer=2, customers=customers
    )
    projects = get_projects(
        projects_per_project_type=1, project_types=project_types
    )

    activities = get_activities(activities_amount=20)

    related_information = {
        TimeTrackerEntities.CUSTOMER.value: customers,
        TimeTrackerEntities.PROJECT_TYPE.value: project_types,
        TimeTrackerEntities.PROJECT.value: projects,
        TimeTrackerEntities.ACTIVITY.value: activities,
    }

    return related_information


def generate_entries_per_user(
    daily_entries_amount: int,
    entries_amount: int,
    owner_id: str,
    projects: List[ProjectFactory],
    activities: List[ActivityFactory],
) -> List[TimeEntryFactory]:

    utc_format = '%Y-%m-%dT%H:%M:%SZ'
    entries_per_user = []
    daily_entries = 0
    projects_ids = [project.id for project in projects]
    activities_ids = [activity.id for activity in activities]

    reference_datetime = get_reference_datetime(
        entries_amount=entries_amount,
        daily_entries_amount=daily_entries_amount,
    )

    for index in range(entries_amount):
        project_id = get_random_element_from_list(projects_ids)
        activity_id = get_random_element_from_list(activities_ids)
        start_date = reference_datetime + timedelta(minutes=1)

        if daily_entries == daily_entries_amount:
            start_date = get_next_day_from_datetime(reference_date=start_date)
            daily_entries = 0

        end_date = get_time_entry_end_date(start_date)

        current_entry = TimeEntryFactory(
            start_date=start_date.strftime(utc_format),
            end_date=end_date.strftime(utc_format),
            owner_id=owner_id,
            project_id=project_id,
            activity_id=activity_id,
        )

        entries_per_user.append(current_entry)
        daily_entries += 1
        reference_datetime = end_date

    return entries_per_user


def get_entry_json(time_entry_factory: TimeEntryFactory) -> dict:
    time_entry = {
        'project_id': time_entry_factory.project_id,
        'activity_id': time_entry_factory.activity_id,
        'technologies': time_entry_factory.technologies,
        'description': time_entry_factory.description,
        'start_date': time_entry_factory.start_date,
        'owner_id': time_entry_factory.owner_id,
        'id': time_entry_factory.id,
        'tenant_id': time_entry_factory.tenant_id,
        'end_date': time_entry_factory.end_date,
    }
    return time_entry
