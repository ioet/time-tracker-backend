from unittest.mock import patch
from utils.extend_model import add_custom_attribute


@patch('time_tracker_api.project_types.project_types_model.create_dao')
@patch('time_tracker_api.customers.customers_model.create_dao')
def test_add_custom_attribute(customers_create_dao, projects_create_dao):
    @add_custom_attribute('project_type', projects_create_dao)
    @add_custom_attribute('customer', customers_create_dao)
    @patch('time_tracker_api.projects.projects_model.ProjectCosmosDBModel')
    def fn(project):
        project.return_value.name = ("Franklin, Mcdonald and Morrison",)
        project.return_value.description = (
            "Include speech feeling court almost country smile economy. True quality mention key. Similar provide yard.",
        )
        project.return_value.customer_id = (
            "9afbfa3a-9de4-4b90-a1b7-a53d2c17a178",
        )
        project.return_value.project_type_id = (
            "208aadb7-1ec1-4a67-a0b0-e0308d27045b",
        )
        project.return_value.technologies = (
            "['python', 'restplus', 'openapi']",
        )
        project.return_value.status = ("active",)
        project.return_value.customer_name = ("Tucker Inc",)
        project.return_value.id = ("768c924e-4501-457f-99c5-7198440d3c60",)
        project.return_value.tenant_id = (
            "e2953984-03e7-4730-be29-1753d24df3b0",
        )
        project.return_value.deleted = (None,)

        return project.return_value

    project = fn().__dict__

    assert 'customer' in project
    assert 'project_type' in project
