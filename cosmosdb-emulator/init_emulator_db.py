from azure.cosmos import exceptions, CosmosClient, PartitionKey
import os, sys, json

with open('/usr/src/app/cosmosdb-emulator/seed_database.json') as database_file:
    seed_database=json.load(database_file)

sys.path.append("/usr/src/app")

DATABASE_ACCOUNT_URI = os.environ.get('DATABASE_ACCOUNT_URI')
DATABASE_MASTER_KEY = os.environ.get('DATABASE_MASTER_KEY')

endpoint = DATABASE_ACCOUNT_URI
key = DATABASE_MASTER_KEY

# <create_cosmos_client>
client = CosmosClient(endpoint, key)
# <create_database_if_not_exists>
database_name = 'time-tracker-db'
database = client.create_database_if_not_exists(id=database_name)
# </create_containers_if_not_exists>

print("Creating TimeTracker initial initial database schema...")

try:
    print('- Project')
    from time_tracker_api.projects.projects_model import container_definition as project_definition
    project_container=database.create_container_if_not_exists(**project_definition)
    for project in seed_database['projects']:
        project_container.create_item(body=project)

    print('- Project type')
    from time_tracker_api.project_types.project_types_model import container_definition as project_type_definition
    project_type_container=database.create_container_if_not_exists(**project_type_definition)
    for project_type in seed_database['project_types']:
        project_type_container.create_item(body=project_type)

    print('- Activity')
    from time_tracker_api.activities.activities_model import container_definition as activity_definition
    activity_container=database.create_container_if_not_exists(**activity_definition)
    for activity in seed_database['activities']:
        activity_container.create_item(body=activity)

    print('- Customer')
    from time_tracker_api.customers.customers_model import container_definition as customer_definition
    customer_container=database.create_container_if_not_exists(**customer_definition)
    for customer in seed_database['customers']:
        customer_container.create_item(body=customer)

    print('- Time entry')
    from time_tracker_api.time_entries.time_entries_model import container_definition as time_entry_definition
    time_entry_container=database.create_container_if_not_exists(**time_entry_definition)
    for time_entry in seed_database['time_entries']:
        time_entry_container.create_item(body=time_entry)

    print('- Technology')
    from time_tracker_api.technologies.technologies_model import container_definition as technologies_definition
    database.create_container_if_not_exists(**technologies_definition)
except exceptions.CosmosResourceExistsError as e:
    print("Unexpected error while creating initial database schema: %s" % e.message)

database_file.close()

print("Done!")

