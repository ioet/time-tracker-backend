import sys

from cosmosdb_emulator.time_tracker_cli.enums.entites import (
    TimeTrackerEntities,
)
from cosmosdb_emulator.time_tracker_cli.questions.common import (
    ask_delete_confirmation,
)
from cosmosdb_emulator.time_tracker_cli.strategies.management_strategy import (
    ManagementStrategy,
)

from cosmosdb_emulator.time_tracker_cli.questions.entries import (
    ask_delete_entries,
    ask_entry_type,
    ask_user_identifier,
    ask_entries_owners_amount,
    ask_entries_amount,
)
from cosmosdb_emulator.time_tracker_cli.utils.common import (
    get_unique_elements_from_list,
)

from cosmosdb_emulator.time_tracker_cli.utils.time_entry import (
    get_related_information_for_entries,
    generate_entries_per_user,
    get_time_tracker_users_ids,
)


class TimeEntryManagementStrategy(ManagementStrategy):

    _conflict_entities: set = {
        TimeTrackerEntities.TIME_ENTRY.value,
    }

    def get_answers_needed_to_create_data(self) -> dict:
        user_agree_to_delete_entries = ask_delete_entries()

        if not user_agree_to_delete_entries:
            print('Thanks for coming! See you later')
            sys.exit()

        entries_type = ask_entry_type()
        entry_owners = []
        own_entries_type_id = 'OE'

        if entries_type == own_entries_type_id:
            user_identifier = ask_user_identifier()
            entry_owners.append(user_identifier)
        else:
            print('Be patient, we are loading important information...')
            users_ids = get_time_tracker_users_ids()
            users_amount = len(users_ids)
            print(f'Currently in Time Tracker we are {users_amount} users')
            entries_owners_amount = ask_entries_owners_amount(users_amount)
            entry_owners = get_unique_elements_from_list(
                elements_list=users_ids,
                amount_of_elements=entries_owners_amount,
            )

        entries_amount = ask_entries_amount(entries_type)

        return {'entries_amount': entries_amount, 'entry_owners': entry_owners}

    def get_confirmation_to_delete_data(self) -> bool:
        is_user_agree_to_delete_entries_data = ask_delete_confirmation(
            self.get_conflict_entities()
        )
        return is_user_agree_to_delete_entries_data

    def generate_entities(self, entity_information: dict) -> dict:
        entries = []

        entries_related_information = get_related_information_for_entries()
        projects = entries_related_information.get(
            TimeTrackerEntities.PROJECT.value
        )
        activities = entries_related_information.get(
            TimeTrackerEntities.ACTIVITY.value
        )

        entries_amount = entity_information.get('entries_amount')
        entry_owners_ids = entity_information.get('entry_owners')
        daily_entries_amount = 5

        for owner_id in entry_owners_ids:
            user_entries = generate_entries_per_user(
                daily_entries_amount=daily_entries_amount,
                entries_amount=entries_amount,
                owner_id=owner_id,
                projects=projects,
                activities=activities,
            )
            entries.extend(user_entries)

        entities = entries_related_information
        entities[TimeTrackerEntities.TIME_ENTRY.value] = entries

        return entities

    def get_conflict_entities(self) -> set:
        return self._conflict_entities
