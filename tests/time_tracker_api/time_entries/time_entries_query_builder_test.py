import pytest
from utils.query_builder import CosmosDBQueryBuilder
from time_tracker_api.time_entries.time_entries_query_builder import (
    TimeEntryQueryBuilder,
)
from utils.repository import remove_white_spaces


def test_TimeEntryQueryBuilder_is_subclass_CosmosDBQueryBuilder():
    query_builder = CosmosDBQueryBuilder()
    time_entries_query_builder = TimeEntryQueryBuilder()

    assert issubclass(
        time_entries_query_builder.__class__, query_builder.__class__
    )


def test_add_sql_date_range_condition_should_update_where_list():
    start_date = "2021-03-19T05:07:00.000Z"
    end_date = "2021-03-25T10:00:00.000Z"
    time_entry_query_builder = (
        TimeEntryQueryBuilder().add_sql_date_range_condition(
            {
                "start_date": start_date,
                "end_date": end_date,
            }
        )
    )
    expected_params = [
        {"name": "@start_date", "value": start_date},
        {"name": "@end_date", "value": end_date},
    ]
    assert len(time_entry_query_builder.where_conditions) == 1
    assert len(time_entry_query_builder.parameters) == len(expected_params)
    assert time_entry_query_builder.get_parameters() == expected_params


def test_build_with_add_sql_date_range_condition():
    time_entry_query_builder = (
        TimeEntryQueryBuilder()
        .add_sql_date_range_condition(
            {
                "start_date": "2021-04-19T05:00:00.000Z",
                "end_date": "2021-04-20T10:00:00.000Z",
            }
        )
        .build()
    )

    expected_query = """
                    SELECT * FROM c
                    WHERE ((c.start_date BETWEEN @start_date AND @end_date) OR
                    (c.end_date BETWEEN @start_date AND @end_date))
                    """
    query = time_entry_query_builder.get_query()

    assert remove_white_spaces(query) == remove_white_spaces(expected_query)
    assert len(time_entry_query_builder.where_conditions) == 1
    assert len(time_entry_query_builder.get_parameters()) == 2


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
    """

    builder_query = time_entry_query_builder.get_query()

    assert remove_white_spaces(builder_query) == remove_white_spaces(
        expected_query
    )
