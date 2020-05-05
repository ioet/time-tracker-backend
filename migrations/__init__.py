from azure.cosmos import PartitionKey
from migrate_anything import configure
from migrate_anything.storage import Storage

from commons.data_access_layer.database import EventContext
from commons.data_access_layer.cosmos_db import cosmos_helper, init_app, \
    CosmosDBRepository

from time_tracker_api import create_app


app = create_app('time_tracker_api.config.CLIConfig')

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
        event_ctx = self.create_event_context('create')
        self.repository.create(
            data={
                "id": name,
                "name": name,
                "code": code,
                "app_id": self.app_id
            },
            event_context=event_ctx,
        )

    def list_migrations(self):
        event_ctx = self.create_event_context('read-many')
        migrations = self.repository.find_all(event_context=event_ctx)
        return [
            [item['name'], item['code']] for item in migrations
        ]

    def remove_migration(self, name):
        event_ctx = self.create_event_context('delete-permanently')
        self.repository.delete_permanently(id=name, event_context=event_ctx)

    def create_event_context(
        self,
        action: str = None,
        description: str = None
    ) -> EventContext:
        return EventContext(
            container_id=self.collection_id,
            action=action,
            description=description,
            app_id=self.app_id
        )

configure(storage=CosmosDBStorage("migration", "time-tracker-api"))
