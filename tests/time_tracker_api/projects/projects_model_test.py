from unittest.mock import Mock, patch
import pytest

from commons.data_access_layer.database import EventContext
from time_tracker_api.projects.projects_model import (
    ProjectCosmosDBRepository,
    ProjectCosmosDBModel,
)


@patch(
    'time_tracker_api.projects.projects_model.ProjectCosmosDBRepository.find_partition_key_value'
)
def test_find_all_v2(
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

    result = project_repository.find_all_v2(
        event_context,
        ['id'],
        ['customer_id']
    )
    find_partition_key_value_mock.assert_called_once()
    assert len(result) == 1
    project = result[0]
    assert isinstance(project, ProjectCosmosDBModel)
    assert project.__dict__ == expected_item