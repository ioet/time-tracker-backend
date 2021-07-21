from typing import List

from cosmosdb_emulator.time_tracker_cli.factories.customer_factory import (
    CustomerFactory,
)
from cosmosdb_emulator.time_tracker_cli.factories.project_type_factory import (
    ProjectTypeFactory,
)


def get_project_types(
    project_types_per_customer: int, customers: List[CustomerFactory]
) -> List[ProjectTypeFactory]:
    project_types = []

    for customer in customers:
        for index in range(project_types_per_customer):
            customer_id = customer.id
            project_type = ProjectTypeFactory(customer_id=customer_id)
            project_types.append(project_type)

    return project_types


def get_project_type_json(project_type_factory: ProjectTypeFactory) -> dict:
    project_type = {
        'id': project_type_factory.id,
        'name': project_type_factory.name,
        'description': project_type_factory.description,
        'customer_id': project_type_factory.customer_id,
        'tenant_id': project_type_factory.tenant_id,
    }
    return project_type
