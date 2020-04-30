from azure.cosmos import PartitionKey

container_definition = {  # pragma: no cover
    'id': 'event',
    'partition_key': PartitionKey(path='/tenant_id')
}
