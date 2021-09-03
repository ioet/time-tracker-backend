from typing import List

from cosmosdb_emulator.time_tracker_cli.factories.project_factory import (
    ProjectFactory,
)
from cosmosdb_emulator.time_tracker_cli.factories.project_type_factory import (
    ProjectTypeFactory,
)


def get_projects(
    projects_per_project_type: int, project_types: List[ProjectTypeFactory]
) -> List[ProjectFactory]:
    projects = []

    for project_type in project_types:
        for index in range(projects_per_project_type):
            project = ProjectFactory(
                project_type_id=project_type.id,
                customer_id=project_type.customer_id,
            )
            projects.append(project)

    return projects


def get_project_json(project_factory: ProjectFactory) -> dict:
    project = {
        'id': project_factory.id,
        'name': project_factory.name,
        'description': project_factory.description,
        'customer_id': project_factory.customer_id,
        'project_type_id': project_factory.project_type_id,
        'tenant_id': project_factory.tenant_id,
        'status': project_factory.status,
    }
    return project
