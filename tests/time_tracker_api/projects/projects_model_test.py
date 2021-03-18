from unittest.mock import Mock, patch
import pytest

from commons.data_access_layer.database import EventContext
from time_tracker_api.projects.projects_model import (
    ProjectCosmosDBRepository,
    ProjectCosmosDBModel,
)


@pytest.mark.parametrize(
    "customer_ids_list,expected_result",
    [
        (["id1"], "c.customer_id IN ('id1')"),
        (["id1", "id2"], "c.customer_id IN ('id1', 'id2')"),
        (["id1", "id2", "id3", "id4"], "c.customer_id IN ('id1', 'id2', 'id3', 'id4')"),
    ],
)
def test_create_sql_in_condition(
    project_repository: ProjectCosmosDBRepository, 
    customer_ids_list, 
    expected_result,
):
    result = project_repository.create_sql_customer_id_in_condition(customer_ids_list)
    assert expected_result == result
    

@patch(
    'time_tracker_api.projects.projects_model.ProjectCosmosDBRepository.create_sql_condition_for_visibility'
)
@patch(
    'time_tracker_api.projects.projects_model.ProjectCosmosDBRepository.create_sql_customer_id_in_condition'
)
@patch(
    'time_tracker_api.projects.projects_model.ProjectCosmosDBRepository.find_partition_key_value'
)
def test_find_all_with_customer_id_in_list(
    find_partition_key_value_mock,
    create_sql_customer_id_in_condition_mock,
    create_sql_condition_for_visibility_mock,
    event_context: EventContext,
    project_repository: ProjectCosmosDBRepository,
):
    expected_item = {
        'customer_id': 'id1',
        'name': 'testing',
        'description': 'do some testing',
        'project_type_id': "id2",
        'tenant_id': 'tenantid1',
    }

    query_items_mock = Mock(return_value=[expected_item])
    project_repository.container = Mock()
    project_repository.container.query_items = query_items_mock

    result = project_repository.find_all_with_customer_id_in_list(event_context, [])

    create_sql_condition_for_visibility_mock.assert_called_once()
    create_sql_customer_id_in_condition_mock.assert_called_once()
    find_partition_key_value_mock.assert_called_once()
    query_items_mock.assert_called_once()

    assert len(result) == 1
    project = result[0]
    assert isinstance(project, ProjectCosmosDBModel)
    assert project.__dict__ == expected_item