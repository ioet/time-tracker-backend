import os

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceExistsError

from cosmosdb_emulator.time_tracker_cli.data_target.data_target import (
    DataTarget,
)
from cosmosdb_emulator.time_tracker_cli.enums.entites import (
    TimeTrackerEntities,
)
from cosmosdb_emulator.time_tracker_cli.utils.activity import get_activity_json
from cosmosdb_emulator.time_tracker_cli.utils.customer import get_customer_json
from cosmosdb_emulator.time_tracker_cli.utils.project import get_project_json
from cosmosdb_emulator.time_tracker_cli.utils.project_type import (
    get_project_type_json,
)
from cosmosdb_emulator.time_tracker_cli.utils.time_entry import get_entry_json

from time_tracker_api.customers.customers_model import (
    container_definition as customer_definition,
)
from time_tracker_api.project_types.project_types_model import (
    container_definition as project_type_definition,
)
from time_tracker_api.projects.projects_model import (
    container_definition as project_definition,
)
from time_tracker_api.activities.activities_model import (
    container_definition as activity_definition,
)
from time_tracker_api.time_entries.time_entries_model import (
    container_definition as time_entry_definition,
)

DATABASE_ACCOUNT_URI = os.environ.get('DATABASE_ACCOUNT_URI')
DATABASE_MASTER_KEY = os.environ.get('DATABASE_MASTER_KEY')
DATABASE_NAME = os.environ.get('DATABASE_NAME')


class CosmosDataTarget(DataTarget):
    def __init__(self):
        self.cosmos_client = CosmosClient(
            DATABASE_ACCOUNT_URI, DATABASE_MASTER_KEY
        )
        self.database = self.cosmos_client.create_database_if_not_exists(
            DATABASE_NAME
        )

    @staticmethod
    def get_container_definition_by_entity_name(container_name: str) -> dict:
        containers_definition = {
            TimeTrackerEntities.CUSTOMER.value: customer_definition,
            TimeTrackerEntities.PROJECT_TYPE.value: project_type_definition,
            TimeTrackerEntities.PROJECT.value: project_definition,
            TimeTrackerEntities.ACTIVITY.value: activity_definition,
            TimeTrackerEntities.TIME_ENTRY.value: time_entry_definition,
        }

        return containers_definition.get(container_name)

    @staticmethod
    def get_json_method_entity_name(entity_name):
        available_json = {
            TimeTrackerEntities.CUSTOMER.value: get_customer_json,
            TimeTrackerEntities.PROJECT_TYPE.value: get_project_type_json,
            TimeTrackerEntities.PROJECT.value: get_project_json,
            TimeTrackerEntities.ACTIVITY.value: get_activity_json,
            TimeTrackerEntities.TIME_ENTRY.value: get_entry_json,
        }

        return available_json.get(entity_name)

    def delete(self, entities: dict):
        for entity in entities:
            entity_container_definition = (
                CosmosDataTarget.get_container_definition_by_entity_name(
                    entity
                )
            )
            entity_container_id = entity_container_definition.get('id')
            self.database.create_container_if_not_exists(
                **entity_container_definition
            )
            self.database.delete_container(entity_container_id)

    def save(self, entities: dict):
        for entity in entities:
            entity_container_definition = (
                CosmosDataTarget.get_container_definition_by_entity_name(
                    entity
                )
            )
            entities_list = entities.get(entity)
            entity_container = self.database.create_container_if_not_exists(
                **entity_container_definition
            )

            for element in entities_list:
                get_json_entity = CosmosDataTarget.get_json_method_entity_name(
                    entity
                )
                json_entity = get_json_entity(element)
                try:
                    entity_container.create_item(body=json_entity)
                except CosmosResourceExistsError:
                    print(
                        f'The {entity} entity with the ID ({element.id}) already exists, so it has not been created.'
                    )
