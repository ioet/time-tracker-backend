from azure.cosmos import PartitionKey

container_definition = {
    'id': 'event',
    'partition_key': PartitionKey(path='/tenant_id')
}