import sys

project_source = '/usr/src/app'
sys.path.append(project_source)

import click
from pyfiglet import Figlet

from cosmosdb_emulator.time_tracker_cli.strategies.management_strategy import (
    ManagementStrategy,
)
from cosmosdb_emulator.time_tracker_cli.strategies.activity_management_strategy import (
    ActivityManagementStrategy,
)
from cosmosdb_emulator.time_tracker_cli.strategies.time_entry_management_strategy import (
    TimeEntryManagementStrategy,
)
from cosmosdb_emulator.time_tracker_cli.strategies.project_management_strategy import (
    ProjectManagementStrategy,
)
from cosmosdb_emulator.time_tracker_cli.strategies.customer_management_strategy import (
    CustomerManagementStrategy,
)
from cosmosdb_emulator.time_tracker_cli.strategies.project_type_management_strategy import (
    ProjectTypeManagementStrategy,
)
from cosmosdb_emulator.time_tracker_cli.strategies.management_context import (
    ManagementContext,
)
from cosmosdb_emulator.time_tracker_cli.enums.entites import (
    TimeTrackerEntities,
)
from cosmosdb_emulator.time_tracker_cli.questions.common import (
    ask_entity,
    time_tracker_entities,
    ask_action,
    entities_actions,
)
from cosmosdb_emulator.time_tracker_cli.data_target.cosmos import (
    CosmosDataTarget,
)


@click.command()
@click.option(
    '--action',
    '-a',
    type=click.Choice(entities_actions, case_sensitive=True),
    help='Action to be implemented in the entities.',
)
@click.option(
    '--entity',
    '-e',
    type=click.Choice(time_tracker_entities, case_sensitive=True),
    help='Entity to which the action is to be applied',
)
def main(action: str, entity: str):
    time_tracker_cli_header = Figlet(font='slant').renderText(
        'Time Tracker CLI'
    )
    print(time_tracker_cli_header)

    selected_action = action if action else ask_action()
    selected_entity = entity if entity else ask_entity(action=selected_action)

    management_strategy = get_strategy_by_selected_entity(selected_entity)
    data_target = CosmosDataTarget()
    management_context = ManagementContext(management_strategy, data_target)

    if selected_action == 'Delete':
        management_context.delete_data()
        sys.exit()

    management_context.create_data()


def get_strategy_by_selected_entity(selected_entity) -> ManagementStrategy:
    strategies = {
        TimeTrackerEntities.TIME_ENTRY.value: TimeEntryManagementStrategy(),
        TimeTrackerEntities.PROJECT.value: ProjectManagementStrategy(),
        TimeTrackerEntities.ACTIVITY.value: ActivityManagementStrategy(),
        TimeTrackerEntities.CUSTOMER.value: CustomerManagementStrategy(),
        TimeTrackerEntities.PROJECT_TYPE.value: ProjectTypeManagementStrategy(),
    }

    return strategies.get(selected_entity)


if __name__ == '__main__':
    main()
