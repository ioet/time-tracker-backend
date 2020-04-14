from azure.cosmos import PartitionKey
from migrate_anything import configure
from migrate_anything.storage import Storage

from time_tracker_api import create_app


class CustomStorage(object):
    def __init__(self, file):
        self.file = file

    def save_migration(self, name, code):
        with open(self.file, "a", encoding="utf-8") as file:
            file.write("{},{}\n".format(name, code))

    def list_migrations(self):
        try:
            with open(self.file, encoding="utf-8") as file:
                return [
                    line.split(",")
                    for line in file.readlines()
                    if line.strip()  # Skip empty lines
                ]
        except FileNotFoundError:
            return []

    def remove_migration(self, name):
        migrations = [
            migration for migration in self.list_migrations() if migration[0] != name
        ]

        with open(self.file, "w", encoding="utf-8") as file:
            for row in migrations:
                file.write("{},{}\n".format(*row))


app = create_app('time_tracker_api.config.CLIConfig')
from commons.data_access_layer.cosmos_db import cosmos_helper, init_app, CosmosDBRepository

if cosmos_helper is None:
    init_app(app)
    from commons.data_access_layer.cosmos_db import cosmos_helper


class CosmosDBStorage(Storage):
    def __init__(self, collection_id, app_id):
        self.collection_id = collection_id
        self.app_id = app_id
        migrations_definition = {
            'id': collection_id,
            'partition_key': PartitionKey(path='/app_id'),
            'unique_key_policy': {
                'uniqueKeys': [
                    {'paths': ['/name']},
                ]
            }
        }
        cosmos_helper.create_container_if_not_exists(migrations_definition)
        self.repository = CosmosDBRepository.from_definition(migrations_definition)

    def save_migration(self, name, code):
        self.repository.create({"id": name,
                                "name": name,
                                "code": code,
                                "app_id": self.app_id})

    def list_migrations(self):
        migrations = self.repository.find_all(self.app_id)
        return [
            [item['name'], item['code']] for item in migrations
        ]

    def remove_migration(self, name):
        self.repository.delete_permanently(name, self.app_id)


configure(storage=CosmosDBStorage("migration", "time-tracker-api"))
