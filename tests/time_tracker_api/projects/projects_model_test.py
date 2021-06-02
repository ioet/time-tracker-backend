from unittest.mock import Mock, patch
from commons.data_access_layer.cosmos_db import CosmosDBDao
from commons.data_access_layer.database import EventContext
from time_tracker_api.customers.customers_model import (
    CustomerCosmosDBModel,
    CustomerCosmosDBDao,
)
from time_tracker_api.projects.projects_model import (
    ProjectCosmosDBRepository,
    ProjectCosmosDBModel,
    create_dao,
)


@patch(
    'time_tracker_api.projects.projects_model.ProjectCosmosDBRepository.find_partition_key_value'
)
def test_find_all_projects_new_version(
    find_partition_key_value_mock,
    event_context: EventContext,
    project_repository: ProjectCosmosDBRepository,
):
    expected_item = {
        'customer_id': 'id1',
        'id': 'id2',
        'name': 'testing',
        'description': 'do some testing',
        'project_type_id': "id2",
        'tenant_id': 'tenantid1',
    }
    query_items_mock = Mock(return_value=[expected_item])
    project_repository.container = Mock()
    project_repository.container.query_items = query_items_mock

    result = project_repository.find_all(
        event_context=event_context,
        conditions={"customer_id": "1"},
        project_ids=['id'],
        customer_ids=['customer_id'],
    )
    find_partition_key_value_mock.assert_called_once()
    assert len(result) == 1
    project = result[0]
    assert isinstance(project, ProjectCosmosDBModel)
    assert project.__dict__ == expected_item


def test_get_project_with_their_customer(
    mocker,
):
    project_data = {
        'customer_id': 'dsakldh12ASD',
        'id': 'JDKASDH12837',
        'name': 'testing',
        'description': 'do some testing',
        'project_type_id': "id2",
        'tenant_id': 'tenantid1',
    }

    customer_data = {
        "id": "dsakldh12ASD",
        "name": 'IOET inc.',
        "description": 'nomatter',
        "tenant_id": 'nomatter',
    }

    cosmos_db_get_mock = mocker.patch.object(CosmosDBDao, 'get')
    customer_db_get_mock = mocker.patch.object(CustomerCosmosDBDao, 'get')

    expected_customer = CustomerCosmosDBModel(customer_data)
    expected_project = ProjectCosmosDBModel(project_data)

    cosmos_db_get_mock.return_value = expected_project
    customer_db_get_mock.return_value = expected_customer

    project = create_dao().get('nomatterid')

    assert isinstance(project, ProjectCosmosDBModel)
    assert project.__dict__['customer_name'] == customer_data['name']
