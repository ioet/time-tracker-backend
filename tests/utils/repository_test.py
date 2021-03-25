from unittest.mock import patch
from utils.repository import convert_list_to_tuple_string, create_sql_in_condition
import pytest


@pytest.mark.parametrize(
    "ids_list",
    [
        123,
        (1, 2),
        "ids_list",
        {"ids_list": []},
    ],
)
def test_convert_list_to_tuple_string_should_fail(ids_list):
    try:
        convert_list_to_tuple_string(ids_list)
    except Exception as e:
        assert type(e) is AssertionError


@pytest.mark.parametrize(
    "ids_list,expected_result",
    [
        (["id1"], "('id1')"),
        (["id1", "id2"], "('id1', 'id2')"),
        (["id1", "id2", "id3", "id4"], "('id1', 'id2', 'id3', 'id4')"),
    ],
)
def test_convert_list_to_tuple_string_should_success(
    ids_list,
    expected_result,
):
    result = convert_list_to_tuple_string(ids_list)

    assert expected_result == result


@pytest.mark.parametrize(
    "field,values,expected_result",
    [
        ("customer_id", ["id1"], "c.customer_id IN ('id1')"),
        ("customer_id", ["id1", "id2"], "c.customer_id IN ('id1', 'id2')"),
        ("customer_id", ["id1", "id2", "id3", "id4"], "c.customer_id IN ('id1', 'id2', 'id3', 'id4')"),
        ("id", ["id1"], "c.id IN ('id1')"),
        ("id", ["id1", "id4"], "c.id IN ('id1', 'id4')"),
        ("id", ["id1", "id2", "id3", "id4"], "c.id IN ('id1', 'id2', 'id3', 'id4')"),
    ],
)
def test_create_sql_in_condition(
    field,
    values,
    expected_result,
):
    result = create_sql_in_condition(field, values)
    assert expected_result == result