from unittest.mock import patch
from utils.query_builder import CosmosDBQueryBuilder
from utils.repository import remove_white_spaces
import pytest


@pytest.mark.parametrize(
    "condition_list, expected_select_condition",
    [
        (None, ["*"]),
        ([], ["*"]),
        (["*"], ["*"]),
        (["c.id"], ["c.id"]),
        (["c.id", "c.name"], ["c.id", "c.name"]),
    ],
)
def test_add_select_conditions_should_update_select_list(
    condition_list, expected_select_condition
):
    query_builder = CosmosDBQueryBuilder().add_select_conditions(
        condition_list
    )

    assert len(query_builder.select_conditions) == len(
        expected_select_condition
    )
    assert query_builder.select_conditions == expected_select_condition


@pytest.mark.parametrize(
    "attribute,ids_list,expected_where_condition_list",
    [
        ("id", [], []),
        (None, None, []),
        ("id", None, []),
        (None, ["id"], []),
        ("id", ["id"], ["c.id IN ('id')"]),
        ("id", ["id1", "id2"], ["c.id IN ('id1', 'id2')"]),
    ],
)
def test_add_sql_in_condition_should_update_where_list(
    attribute,
    ids_list,
    expected_where_condition_list,
):
    query_builder = CosmosDBQueryBuilder().add_sql_in_condition(
        attribute, ids_list
    )

    assert len(query_builder.where_conditions) == len(
        expected_where_condition_list
    )
    assert query_builder.where_conditions == expected_where_condition_list


@pytest.mark.parametrize(
    "data,expected_where_list,expected_params",
    [
        ({}, [], []),
        ({'id': 1}, ["c.id = @id"], [{'name': "@id", 'value': 1}]),
        (
            {'id': 1, 'name': 'test'},
            ["c.id = @id", "c.name = @name"],
            [{'name': "@id", 'value': 1}, {'name': "@name", 'value': 'test'}],
        ),
    ],
)
def test_add_sql_where_equal_condition_should_update_where_params_list(
    data,
    expected_where_list,
    expected_params,
):
    query_builder = CosmosDBQueryBuilder().add_sql_where_equal_condition(data)

    assert len(query_builder.where_conditions) == len(data)
    assert query_builder.where_conditions == expected_where_list

    assert len(query_builder.parameters) == len(expected_params)
    assert query_builder.parameters == expected_params


def test_add_sql_where_equal_condition_with_None_should_not_update_lists():
    query_builder = CosmosDBQueryBuilder().add_sql_where_equal_condition(None)

    assert len(query_builder.where_conditions) == 0
    assert query_builder.where_conditions == []
    assert len(query_builder.parameters) == 0
    assert query_builder.parameters == []


@pytest.mark.parametrize(
    "visibility_bool,expected_where_list",
    [(True, ['NOT IS_DEFINED(c.deleted)']), (False, [])],
)
def test_add_sql_visibility_condition(
    visibility_bool,
    expected_where_list,
):
    query_builder = CosmosDBQueryBuilder().add_sql_visibility_condition(
        visibility_bool
    )

    assert len(query_builder.where_conditions) == len(expected_where_list)
    assert query_builder.where_conditions == expected_where_list


@pytest.mark.parametrize(
    "limit_value,expected_limit",
    [
        (1, 1),
        (10, 10),
        (None, None),
    ],
)
def test_add_sql_limit_condition(limit_value, expected_limit):
    query_builder = CosmosDBQueryBuilder().add_sql_limit_condition(limit_value)

    assert query_builder.limit == expected_limit


@pytest.mark.parametrize(
    "offset_value,expected_offset",
    [
        (1, 1),
        (10, 10),
        (None, None),
    ],
)
def test_add_sql_offset_condition(
    offset_value,
    expected_offset,
):
    query_builder = CosmosDBQueryBuilder().add_sql_offset_condition(
        offset_value
    )

    assert query_builder.offset == expected_offset


@pytest.mark.parametrize(
    "select_conditions,expected_condition",
    [
        ([], "*"),
        (["c.id"], "c.id"),
        (["c.id", "c.name"], "c.id,c.name"),
    ],
)
def test__build_select_return_fields_in_select_list(
    select_conditions,
    expected_condition,
):
    query_builder = CosmosDBQueryBuilder().add_select_conditions(
        select_conditions
    )

    result = query_builder._CosmosDBQueryBuilder__build_select()
    assert result == expected_condition


@pytest.mark.parametrize(
    "where_dict,expected_condition",
    [
        ({"id": 1}, "WHERE c.id = @id"),
        ({"id": 1, "name": "test"}, "WHERE c.id = @id AND c.name = @name"),
    ],
)
def test__build_where_should_return_concatenate_conditions(
    where_dict,
    expected_condition,
):
    query_builder = CosmosDBQueryBuilder().add_sql_where_equal_condition(
        where_dict
    )

    result = query_builder._CosmosDBQueryBuilder__build_where()

    assert result == expected_condition


@pytest.mark.parametrize(
    "offset,expected_condition,expected_params",
    [(1, "OFFSET @offset", [{'name': '@offset', 'value': 1}]), (None, "", [])],
)
def test__build_offset(
    offset,
    expected_condition,
    expected_params,
):
    query_builder = CosmosDBQueryBuilder().add_sql_offset_condition(offset)

    result = query_builder._CosmosDBQueryBuilder__build_offset()
    assert result == expected_condition
    assert len(query_builder.parameters) == len(expected_params)
    assert query_builder.get_parameters() == expected_params


@pytest.mark.parametrize(
    "limit,expected_condition,expected_params",
    [(1, "LIMIT @limit", [{'name': '@limit', 'value': 1}]), (None, "", [])],
)
def test__build_limit(
    limit,
    expected_condition,
    expected_params,
):
    query_builder = CosmosDBQueryBuilder().add_sql_limit_condition(limit)

    result = query_builder._CosmosDBQueryBuilder__build_limit()
    assert result == expected_condition
    assert len(query_builder.parameters) == len(expected_params)
    assert query_builder.get_parameters() == expected_params


def test_build_with_all_calls_return_query_with_all_conditions():
    query_builder = (
        CosmosDBQueryBuilder()
        .add_select_conditions(["c.description"])
        .add_sql_in_condition("id", ["id1", "id2"])
        .add_sql_where_equal_condition({'name': 'test'})
        .add_sql_offset_condition(2)
        .add_sql_limit_condition(10)
        .add_sql_visibility_condition(True)
        .build()
    )
    query = query_builder.get_query()
    expected_query = """
                    SELECT c.description FROM c
                    WHERE c.id IN ('id1', 'id2') AND c.name = @name AND NOT IS_DEFINED(c.deleted)
                    OFFSET @offset
                    LIMIT @limit
                    """

    assert remove_white_spaces(query) == remove_white_spaces(expected_query)
    assert len(query_builder.get_parameters()) > 0
    assert len(query_builder.where_conditions) > 0
    assert len(query_builder.select_conditions) > 0


def test_build_with_empty_and_None_attributes_return_query_select_all():

    query_builder = (
        CosmosDBQueryBuilder()
        .add_select_conditions()
        .add_sql_in_condition()
        .add_sql_where_equal_condition()
        .add_sql_limit_condition(None)
        .add_sql_offset_condition(None)
        .build()
    )

    query = query_builder.get_query()
    expected_query = """SELECT * FROM c"""

    query = remove_white_spaces(query)
    expected_query = remove_white_spaces(expected_query)

    assert query == expected_query
    assert len(query_builder.get_parameters()) == 0
    assert len(query_builder.where_conditions) == 0
