from unittest.mock import Mock, patch
from commons.data_access_layer.cosmos_db import CosmosDBDao
from commons.data_access_layer.database import EventContext
from time_tracker_api.customers.customers_model import (
    CustomerCosmosDBModel,
    CustomerCosmosDBDao,
)
from time_tracker_api.project_types.project_types_model import (
    ProjectTypeCosmosDBModel,
    ProjectTypeCosmosDBDao,
)
from time_tracker_api.projects.projects_model import (
    ProjectCosmosDBRepository,
    ProjectCosmosDBModel,
    create_dao,
)
from faker import Faker

fake = Faker()


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


def test_get_all_projects_with_customers(
    mocker,
):
    customer_id = fake.uuid4()
    project_type_id = fake.uuid4()

    customer_data = {
        'id': customer_id,
        'name': fake.company(),
        'description': fake.paragraph(),
        'tenant_id': fake.uuid4(),
    }

    project_data = {
        'customer_id': customer_id,
        'id': fake.uuid4(),
        'name': fake.company(),
        'description': fake.paragraph(),
        'project_type_id': project_type_id,
        'tenant_id': fake.uuid4(),
    }

    project_type_dao = {
        'id': project_type_id,
        'name': fake.name(),
        'description': fake.paragraph(),
        'tenant_id': fake.uuid4(),
    }

    expected_customer = CustomerCosmosDBModel(customer_data)
    expected_project = ProjectCosmosDBModel(project_data)
    expected_project_type = ProjectTypeCosmosDBModel(project_type_dao)

    customer_dao_get_all_mock = mocker.patch.object(
        CustomerCosmosDBDao, 'get_all'
    )
    customer_dao_get_all_mock.return_value = [expected_customer]

    projects_repository_find_all_mock = mocker.patch.object(
        ProjectCosmosDBRepository, 'find_all'
    )
    projects_repository_find_all_mock.return_value = [expected_project]

    project_type_dao_get_all_mock = mocker.patch.object(
        ProjectTypeCosmosDBDao, 'get_all'
    )
    project_type_dao_get_all_mock.return_value = [expected_project_type]
    projects = create_dao().get_all()

    assert isinstance(projects[0], ProjectCosmosDBModel)
    assert projects[0].__dict__['customer_name'] == customer_data['name']
    assert len(projects) == 1
