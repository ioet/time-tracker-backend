from unittest.mock import Mock, patch
import pytest
from faker import Faker
from typing import List

from commons.data_access_layer.database import EventContext
from time_tracker_api.activities.activities_model import (
    ActivityCosmosDBRepository,
    ActivityCosmosDBModel,
)


@pytest.mark.parametrize(
    "id_list", [123, (1, 2), "id_list", {"id_list": []},],
)
def test_validate_list(
    id_list, activity_repository: ActivityCosmosDBRepository
):
    try:
        activity_repository.validate_list(id_list)
    except Exception as e:
        assert type(e) is AssertionError


@patch(
    'time_tracker_api.activities.activities_model.ActivityCosmosDBRepository.validate_list'
)
@pytest.mark.parametrize(
    "id_list,expected_result",
    [
        (["id1"], '("id1")'),
        (["id1", "id2"], "('id1', 'id2')"),
        (["id1", "id2", "id3", "id4"], "('id1', 'id2', 'id3', 'id4')"),
    ],
)
def test_convert_list_to_tuple_string(
    validate_list_mock,
    activity_repository: ActivityCosmosDBRepository,
    id_list,
    expected_result,
):
    result = activity_repository.convert_list_to_tuple_string(id_list)

    validate_list_mock.assert_called_once()
    assert expected_result == result


@pytest.mark.parametrize(
    "id_list,expected_result",
    [
        (["id1"], 'c.id IN ("id1")'),
        (["id1", "id2"], "c.id IN ('id1', 'id2')"),
        (["id1", "id2", "id3", "id4"], "c.id IN ('id1', 'id2', 'id3', 'id4')"),
    ],
)
def test_create_sql_in_condition(
    activity_repository: ActivityCosmosDBRepository, id_list, expected_result,
):
    result = activity_repository.create_sql_in_condition(id_list)
    assert expected_result == result


@patch(
    'time_tracker_api.activities.activities_model.ActivityCosmosDBRepository.create_sql_condition_for_visibility'
)
@patch(
    'time_tracker_api.activities.activities_model.ActivityCosmosDBRepository.create_sql_in_condition'
)
@patch(
    'time_tracker_api.activities.activities_model.ActivityCosmosDBRepository.find_partition_key_value'
)
def test_find_all_with_id_in_list(
    find_partition_key_value_mock,
    create_sql_in_condition_mock,
    create_sql_condition_for_visibility_mock,
    event_context: EventContext,
    activity_repository: ActivityCosmosDBRepository,
):
    expected_item = {
        'id': 'id1',
        'name': 'testing',
        'description': 'do some testing',
        'tenant_id': 'tenantid1',
    }

    query_items_mock = Mock(return_value=[expected_item])
    activity_repository.container = Mock()
    activity_repository.container.query_items = query_items_mock

    result = activity_repository.find_all_with_id_in_list(event_context, [])

    create_sql_condition_for_visibility_mock.assert_called_once()
    create_sql_in_condition_mock.assert_called_once()
    find_partition_key_value_mock.assert_called_once()
    query_items_mock.assert_called_once()

    assert len(result) == 1
    activity = result[0]
    assert isinstance(activity, ActivityCosmosDBModel)
    assert activity.__dict__ == expected_item
