from unittest.mock import patch
from utils.repository import convert_list_to_tuple_string, validate_list
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
def test_validate_list(ids_list):
    try:
        validate_list(ids_list)
    except Exception as e:
        assert type(e) is AssertionError


@patch('utils.repository.validate_list')
@pytest.mark.parametrize(
    "ids_list,expected_result",
    [
        (["id1"], "('id1')"),
        (["id1", "id2"], "('id1', 'id2')"),
        (["id1", "id2", "id3", "id4"], "('id1', 'id2', 'id3', 'id4')"),
    ],
)
def test_convert_list_to_tuple_string(
    validate_list_mock,
    ids_list,
    expected_result,
):
    result = convert_list_to_tuple_string(ids_list)

    validate_list_mock.assert_called_once()
    assert expected_result == result
