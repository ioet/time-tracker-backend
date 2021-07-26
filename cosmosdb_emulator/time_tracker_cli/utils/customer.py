from typing import List

from cosmosdb_emulator.time_tracker_cli.factories.customer_factory import (
    CustomerFactory,
)


def get_customers(customer_amount: int) -> List[CustomerFactory]:
    customers = CustomerFactory.create_batch(customer_amount)
    return customers


def get_customer_json(customer_factory: CustomerFactory) -> dict:
    customer = {
        'id': customer_factory.id,
        'name': customer_factory.name,
        'description': customer_factory.description,
        'tenant_id': customer_factory.tenant_id,
    }
    return customer
