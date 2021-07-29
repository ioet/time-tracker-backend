import pytest
from utils.query_builder import CosmosDBQueryBuilder
from time_tracker_api.time_entries.time_entries_query_builder import (
    TimeEntryQueryBuilder,
)
from utils.repository import remove_white_spaces


def test_time_entry_query_builder_should_be_subclass_of_cosmos_query_builder():
    query_builder = CosmosDBQueryBuilder()
    time_entries_query_builder = TimeEntryQueryBuilder()

    assert issubclass(
        time_entries_query_builder.__class__, query_builder.__class__
    )


def test_add_sql_interception_with_date_range_condition():
    start_date = "2021-01-19T05:07:00.000Z"
    end_date = "2021-01-25T10:00:00.000Z"

    time_entry_query_builder = (
        TimeEntryQueryBuilder().add_sql_interception_with_date_range_condition(
            start_date, end_date
        )
    )

    expected_params = [
        {"name": "@start_date", "value": start_date},
        {"name": "@end_date", "value": end_date},
    ]

    assert len(time_entry_query_builder.where_conditions) == 1
    assert len(time_entry_query_builder.parameters) == len(expected_params)
    assert time_entry_query_builder.parameters == expected_params


def test_build_with_add_sql_interception_with_date_range_condition():
    start_date = "2021-02-19T05:07:00.000Z"
    end_date = "2021-02-25T10:00:00.000Z"
    time_entry_query_builder = (
        TimeEntryQueryBuilder()
        .add_sql_interception_with_date_range_condition(start_date, end_date)
        .build()
    )

    expected_query = """
        SELECT * FROM c
        WHERE (((c.start_date BETWEEN @start_date AND @end_date)
          OR (c.end_date BETWEEN @start_date AND @end_date))
          OR ((@start_date BETWEEN c.start_date AND c.end_date)
          OR (@end_date BETWEEN c.start_date AND c.end_date)))
          AND c.start_date!= @end_date
          AND c.end_date!= @start_date
    """

    builder_query = time_entry_query_builder.get_query()

    assert remove_white_spaces(builder_query) == remove_white_spaces(
        expected_query
    )


def test_add_sql_is_running_time_entry_condition_should_update_where_conditions_list():
    query_builder = (
        TimeEntryQueryBuilder().add_sql_is_running_time_entry_condition()
    )

    assert len(query_builder.where_conditions) == 1


@pytest.mark.parametrize(
    "expected_condition,expected_params",
    [("c.id!=@ignore_id", {"name": "@ignore_id", "value": "nomatter"})],
)
def test_add_sql_ignore_id_condition_should_update_where_conditions_list(
    expected_condition, expected_params
):
    query_builder = TimeEntryQueryBuilder().add_sql_ignore_id_condition(
        'nomatter'
    )

    assert len(query_builder.where_conditions) == 1
    assert len(query_builder.parameters) == 1
    assert query_builder.where_conditions[0].strip() == expected_condition
    assert query_builder.parameters[0] == expected_params
