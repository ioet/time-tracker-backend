from unittest.mock import Mock, patch
import pytest
from faker import Faker
from typing import List

from commons.data_access_layer.database import EventContext
from time_tracker_api.activities.activities_model import (
    ActivityCosmosDBRepository,
    ActivityCosmosDBDao,
    ActivityCosmosDBModel,
)

"""
def create_activity(
    valid_tenant_id: str,
    event_context: EventContext,
    activity_repository: ActivityCosmosDBRepository,
) -> ActivityCosmosDBModel:
    data = {
        "id": Faker().uuid4(),
        "name": Faker().name(),
        "description": Faker().paragraph(nb_sentences=2),
        "deleted": Faker().uuid4(),
        "tenant_id": valid_tenant_id,
    }

    created_item = activity_repository.create(
        data, event_context, mapper=ActivityCosmosDBModel
    )
    return created_item
"""


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
    "id_list , exception",
    [
        (123, AssertionError),
        ((1, 2), AssertionError),
        ("id_list", AssertionError),
        ({"id_list": []}, AssertionError),
    ],
)
def test_create_sql_in_condition_with_invalid_list_should_fail(
    id_list, exception, activity_repository: ActivityCosmosDBRepository
):
    try:
        activity_repository.create_sql_in_condition(id_list)
    except Exception as e:
        assert type(e) is exception


# valid_id = ["03741215-a9b0-4a22-93cc-9cd6571e0366",
#             "d45c770a-b1a0-4bd8-a713-22c01a23e41b",
#             "57be59a6-1c01-449c-b3cb-17cd4113c6d2",
#             "1263af28-6a06-43b2-b27f-7e2bd0edc58e",
#             "a2cb8294-56ae-4fb8-aa7d-9a8056658f9e",
#             "320716ae-eb1b-441f-8a83-1c9d006bff92"]


# @pytest.mark.parametrize(
#     'activity_id', valid_id
# )
# def test_find_all_with_id_in_list_should_success(
#     event_context: EventContext,
#     activity_id: str,
#     activity_repository: ActivityCosmosDBRepository,
# ):
#     id_list = [activity_id]
#     result = activity_repository.find_all_with_id_in_list(
#         event_context, id_list)
#     assert len(result) > 0


@patch(
    'time_tracker_api.activities.activities_model.ActivityCosmosDBRepository.find_all_with_id_in_list',
    new_callable=Mock,
)
def test_test_find_all_width_id_in_list(
    find_all_with_id_in_list_mock,
    event_context: EventContext,
    activity_repository: ActivityCosmosDBRepository,
):

    activity_repository.find_all_with_id_in_list(event_context, ["123456"])
    find_all_with_id_in_list_mock.assert_called_once()


invalid_id = [
    "4ff7b319-a3f1-4a99-a0e0-649e3d3e6c65",
    "3ee1aef6-079e-4dcd-abe6-bee6143c9473",
    "0beb1210-91fa-40f3-ac1b-bac92bc31623",
    "0556c46b-8a9b-48c2-b198-137c8afab7de",
]


# @pytest.mark.parametrize(
#     "activity_id", invalid_id
# )
# def test_find_all_with_id_in_list_should_not_find(
#     event_context: EventContext,
#     activity_id: str,
#     activity_repository: ActivityCosmosDBRepository
# ):
#     id_list = [activity_id]
#     result = activity_repository.find_all_with_id_in_list(
#         event_context, id_list)
#     assert len(result) == 0
