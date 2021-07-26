from azure.cosmos import exceptions, CosmosClient, PartitionKey
import os, sys

sys.path.append("/usr/src/app")

DATABASE_ACCOUNT_URI = os.environ.get('DATABASE_ACCOUNT_URI')
DATABASE_MASTER_KEY = os.environ.get('DATABASE_MASTER_KEY')
DATABASE_NAME = os.environ.get('DATABASE_NAME')

client = CosmosClient(DATABASE_ACCOUNT_URI, DATABASE_MASTER_KEY)
database = client.create_database_if_not_exists(id=DATABASE_NAME)

print("Creating TimeTracker initial initial database schema...")

try:
    print('- Project')
    from time_tracker_api.projects.projects_model import (
        container_definition as project_definition,
    )

    database.create_container_if_not_exists(**project_definition)

    print('- Project type')
    from time_tracker_api.project_types.project_types_model import (
        container_definition as project_type_definition,
    )

    database.create_container_if_not_exists(**project_type_definition)

    print('- Activity')
    from time_tracker_api.activities.activities_model import (
        container_definition as activity_definition,
    )

    database.create_container_if_not_exists(**activity_definition)

    print('- Customer')
    from time_tracker_api.customers.customers_model import (
        container_definition as customer_definition,
    )

    database.create_container_if_not_exists(**customer_definition)

    print('- Time entry')
    from time_tracker_api.time_entries.time_entries_model import (
        container_definition as time_entry_definition,
    )

    database.create_container_if_not_exists(**time_entry_definition)

    print('- Technology')
    from time_tracker_api.technologies.technologies_model import (
        container_definition as technologies_definition,
    )

    database.create_container_if_not_exists(**technologies_definition)
except exceptions.CosmosResourceExistsError as e:
    print(
        "Unexpected error while creating initial database schema: %s"
        % e.message
    )

print("Done!")
