from commons.data_access_layer.cosmos_db import (
    CosmosDBRepository,
    CustomError,
)

from time_tracker_api.time_entries.time_entries_model import (
    container_definition,
    TimeEntryCosmosDBModel,
)

from utils.time import current_datetime_str
from utils.repository import convert_list_to_tuple_string

from utils.extend_model import (
    add_project_info_to_time_entries,
    add_activity_name_to_time_entries,
    create_in_condition,
    add_user_email_to_time_entries,
)
import flask
from flask_restplus import abort
from flask_restplus._http import HTTPStatus
from utils.azure_users import AzureConnection
from time_tracker_api.activities import activities_model
from commons.data_access_layer.database import EventContext
from typing import List, Callable
from time_tracker_api.projects import projects_model
from time_tracker_api.time_entries.time_entries_query_builder import (
    TimeEntryQueryBuilder,
)
from utils.query_builder import CosmosDBQueryBuilder, Order
from utils.time import str_to_datetime
from utils.validate_entries import are_related_entry_entities_valid


class TimeEntryCosmosDBRepository(CosmosDBRepository):
    def __init__(self):
        CosmosDBRepository.__init__(
            self,
            container_id=container_definition['id'],
            partition_key_attribute='tenant_id',
            order_fields=['start_date DESC'],
            mapper=TimeEntryCosmosDBModel,
        )

    def find_all_entries(
        self,
        event_context: EventContext,
        conditions: dict = None,
        date_range: dict = None,
        **kwargs,
    ):
        conditions = conditions if conditions else {}
        date_range = date_range if date_range else {}

        time_entries = CosmosDBRepository.find_all(
            self,
            event_context=event_context,
            conditions=conditions,
            date_range=date_range,
            max_count=kwargs.get("max_count", None),
            offset=kwargs.get("offset", 0),
        )
        return time_entries

    def count(
        self,
        event_context: EventContext,
        conditions: dict = None,
        owner_ids: list = None,
        date_range: dict = None,
        visible_only=True,
        **kwargs,
    ):
        query_builder = (
            TimeEntryQueryBuilder()
            .add_select_conditions(["VALUE COUNT(1)"])
            .add_sql_in_condition('owner_id', owner_ids)
            .add_sql_where_equal_condition(conditions)
            .add_sql_visibility_condition(visible_only)
            .add_sql_date_range_condition(date_range)
            .build()
        )

        query_str = query_builder.get_query()
        params = query_builder.get_parameters()
        tenant_id_value = self.find_partition_key_value(event_context)
        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=tenant_id_value,
        )

        return result.next()

    def add_complementary_info(
        self, time_entries=None, max_count=None, exist_conditions=False
    ):
        if time_entries:
            project_ids = list(set([x.project_id for x in time_entries]))
            activity_ids = list(set([x.activity_id for x in time_entries]))

            project_dao = projects_model.create_dao()
            projects = project_dao.get_all(
                project_ids=project_ids,
                visible_only=False,
                max_count=max_count,
            )

            add_project_info_to_time_entries(time_entries, projects)

            activity_dao = activities_model.create_dao()
            activities = activity_dao.get_all(
                activities_id=activity_ids,
                visible_only=False,
                max_count=max_count,
            )

            add_activity_name_to_time_entries(time_entries, activities)

            users = AzureConnection().users()
            add_user_email_to_time_entries(time_entries, users)
        elif not time_entries and exist_conditions:
            abort(HTTPStatus.NOT_FOUND, "Time entry not found")
        return time_entries

    def find_all(
        self,
        conditions,
        event_context: EventContext,
        date_range: dict = None,
        owner_ids: list = None,
        test_user_ids=None,
        offset=0,
        max_count=None,
        visible_only=True,
        mapper: Callable = None,
    ):
        max_count = self.get_page_size_or(max_count)
        date_range = date_range if date_range else {}

        query_builder = (
            TimeEntryQueryBuilder()
            .add_sql_in_condition('owner_id', owner_ids)
            .add_sql_where_equal_condition(conditions)
            .add_sql_visibility_condition(visible_only)
            .add_sql_date_range_condition(date_range)
            .add_sql_not_in_condition('owner_id', test_user_ids)
            .add_sql_order_by_condition('start_date', Order.DESC)
            .add_sql_limit_condition(max_count)
            .add_sql_offset_condition(offset)
            .build()
        )

        query_str = query_builder.get_query()
        params = query_builder.get_parameters()
        tenant_id_value = self.find_partition_key_value(event_context)
        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=tenant_id_value,
        )

        function_mapper = self.get_mapper_or_dict(mapper)
        time_entries = list(map(function_mapper, result))
        exist_conditions = len(conditions) > 1

        return self.add_complementary_info(
            time_entries, max_count, exist_conditions
        )

    def get_last_entry(
        self,
        owner_id: str,
        id_running_entry: str,
        event_context: EventContext,
        visible_only=True,
        mapper: Callable = None,
    ):
        query_builder = (
            CosmosDBQueryBuilder()
            .add_sql_where_equal_condition({'owner_id': owner_id})
            .add_sql_order_by_condition('end_date', Order.DESC)
            .add_sql_not_in_condition('id', [id_running_entry])
            .build()
        )
        query_str = query_builder.get_query()
        params = query_builder.get_parameters()
        partition_key_value = self.find_partition_key_value(event_context)
        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=partition_key_value,
        )
        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(next(result))

    def update_last_entry(
        self,
        owner_id: str,
        start_date: str,
        id_running_entry: str,
        event_context: EventContext,
    ):
        last_entry = self.get_last_entry(
            owner_id, id_running_entry, event_context
        )
        end_date = str_to_datetime(last_entry.end_date)
        _start_date = str_to_datetime(start_date)

        if _start_date < end_date:
            update_data = {'end_date': start_date}
            self.partial_update(last_entry.id, update_data, event_context)

    def on_create(self, new_item_data: dict, event_context: EventContext):
        CosmosDBRepository.on_create(self, new_item_data, event_context)

        if new_item_data.get("start_date") is None:
            new_item_data['start_date'] = current_datetime_str()

        self.validate_data(new_item_data, event_context)

    def on_update(self, updated_item_data: dict, event_context: EventContext):
        CosmosDBRepository.on_update(self, updated_item_data, event_context)
        is_update_to_delete = 'deleted' in updated_item_data
        if not is_update_to_delete:
            self.validate_data(updated_item_data, event_context)
        self.replace_empty_value_per_none(updated_item_data)

    def find_interception_with_date_range(
        self,
        start_date,
        end_date,
        owner_id,
        tenant_id,
        ignore_id=None,
        visible_only=True,
        mapper: Callable = None,
    ):
        conditions = {
            "owner_id": owner_id,
            "tenant_id": tenant_id,
        }
        end_date = end_date or current_datetime_str()

        query_builder = (
            TimeEntryQueryBuilder()
            .add_sql_interception_with_date_range_condition(
                start_date, end_date
            )
            .add_sql_where_equal_condition(conditions)
            .add_sql_ignore_id_condition(ignore_id)
            .add_sql_visibility_condition(visible_only)
            .add_sql_order_by_condition('start_date', Order.DESC)
            .build()
        )

        query_str = query_builder.get_query()
        params = query_builder.get_parameters()

        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=tenant_id,
        )

        function_mapper = self.get_mapper_or_dict(mapper)
        collision_entries = list(map(function_mapper, result))
        exist_collision_entries = len(collision_entries) > 0
        return exist_collision_entries

    def find_running(
        self, tenant_id: str, owner_id: str, mapper: Callable = None
    ):
        conditions = {
            "owner_id": owner_id,
            "tenant_id": tenant_id,
        }

        query_builder = (
            TimeEntryQueryBuilder()
            .add_sql_is_running_time_entry_condition()
            .add_sql_where_equal_condition(conditions)
            .add_sql_visibility_condition(True)
            .add_sql_offset_condition(0)
            .add_sql_limit_condition(1)
            .build()
        )

        query_str = query_builder.get_query()
        params = query_builder.get_parameters()

        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=tenant_id,
            max_item_count=1,
        )

        function_mapper = self.get_mapper_or_dict(mapper)
        try:
            return function_mapper(next(result))
        except StopIteration:
            raise CustomError(HTTPStatus.NO_CONTENT)

    def validate_data(self, data, event_context: EventContext):
        start_date = data.get('start_date')

        related_project_id = data.get('project_id')
        related_activity_id = data.get('activity_id')

        are_related_entities_valid = are_related_entry_entities_valid(
            project_id=related_project_id, activity_id=related_activity_id
        )

        if not are_related_entities_valid.get('is_valid'):
            status_code = are_related_entities_valid.get('status_code')
            message = are_related_entities_valid.get('message')
            raise CustomError(
                status_code,
                description=message,
            )

        if data.get('end_date') is not None:
            if data['end_date'] <= start_date:
                raise CustomError(
                    HTTPStatus.BAD_REQUEST,
                    description="You must end the time entry after it started",
                )
            if data['end_date'] >= current_datetime_str():
                raise CustomError(
                    HTTPStatus.BAD_REQUEST,
                    description="You cannot end a time entry in the future",
                )

        exist_collision_entries = self.find_interception_with_date_range(
            start_date=start_date,
            end_date=data.get('end_date'),
            owner_id=event_context.user_id,
            tenant_id=event_context.tenant_id,
            ignore_id=data.get('id'),
        )

        if exist_collision_entries:
            raise CustomError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                description="There is another time entry in that date range",
            )
