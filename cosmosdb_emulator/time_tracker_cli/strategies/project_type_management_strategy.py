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


class ProjectTypeManagementStrategy(ManagementStrategy):

    _conflict_entities: set = {
        TimeTrackerEntities.PROJECT_TYPE.value,
        TimeTrackerEntities.PROJECT.value,
        TimeTrackerEntities.TIME_ENTRY.value,
    }

    def get_confirmation_to_delete_data(self) -> bool:
        is_user_agree_to_delete_project_types_data = ask_delete_confirmation(
            self.get_conflict_entities()
        )
        return is_user_agree_to_delete_project_types_data

    def get_answers_needed_to_create_data(self) -> dict:
        print('This functionality has not yet been implemented')
        sys.exit()

    def generate_entities(self, entity_information: dict) -> dict:
        print('This functionality has not yet been implemented')
        sys.exit()

    def get_conflict_entities(self) -> set:
        return self._conflict_entities
