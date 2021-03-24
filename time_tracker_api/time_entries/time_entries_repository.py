from commons.data_access_layer.cosmos_db import (
    CosmosDBRepository,
    CustomError,
)

from time_tracker_api.time_entries.time_entries_model import (
    container_definition,
    TimeEntryCosmosDBModel,
)

from utils.time import (
    current_datetime_str,
)

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


class TimeEntryCosmosDBRepository(CosmosDBRepository):
    def __init__(self):
        CosmosDBRepository.__init__(
            self,
            container_id=container_definition['id'],
            partition_key_attribute='tenant_id',
            order_fields=['start_date DESC'],
            mapper=TimeEntryCosmosDBModel,
        )

    @staticmethod
    def create_sql_ignore_id_condition(id: str):
        if id is None:
            return ''
        else:
            return "AND c.id!=@ignore_id"

    @staticmethod
    def create_sql_date_range_filter(date_range: dict) -> str:
        if 'start_date' and 'end_date' in date_range:
            return """
            ((c.start_date BETWEEN @start_date AND @end_date) OR
             (c.end_date BETWEEN @start_date AND @end_date))
            """
        else:
            return ''

    def find_all_entries(
        self,
        event_context: EventContext,
        conditions: dict = None,
        custom_sql_conditions: List[str] = None,
        date_range: dict = None,
        **kwargs,
    ):
        conditions = conditions if conditions else {}
        custom_sql_conditions = (
            custom_sql_conditions if custom_sql_conditions else []
        )
        date_range = date_range if date_range else {}

        custom_sql_conditions.append(
            self.create_sql_date_range_filter(date_range)
        )

        custom_params = self.generate_params(date_range)
        time_entries = CosmosDBRepository.find_all(
            self,
            event_context=event_context,
            conditions=conditions,
            custom_sql_conditions=custom_sql_conditions,
            custom_params=custom_params,
            max_count=kwargs.get("max_count", None),
            offset=kwargs.get("offset", 0),
        )
        return time_entries

    def count(
        self,
        event_context: EventContext,
        conditions: dict = None,
        custom_sql_conditions: List[str] = None,
        date_range: dict = None,
        visible_only=True,
        **kwargs,
    ):
        conditions = conditions if conditions else {}
        custom_sql_conditions = (
            custom_sql_conditions if custom_sql_conditions else []
        )
        date_range = date_range if date_range else {}

        custom_sql_conditions.append(
            self.create_sql_date_range_filter(date_range)
        )

        custom_params = self.generate_params(date_range)
        partition_key_value = self.find_partition_key_value(event_context)
        params = [
            {"name": "@partition_key_value", "value": partition_key_value},
        ]
        params.extend(self.generate_params(conditions))
        params.extend(custom_params)

        query_str = """
            SELECT VALUE COUNT(1) FROM c
            WHERE c.{partition_key_attribute}=@partition_key_value
            {conditions_clause}
            {visibility_condition}
            {custom_sql_conditions_clause}
            """.format(
            partition_key_attribute=self.partition_key_attribute,
            visibility_condition=self.create_sql_condition_for_visibility(
                visible_only
            ),
            conditions_clause=self.create_sql_where_conditions(conditions),
            custom_sql_conditions_clause=self.create_custom_sql_conditions(
                custom_sql_conditions
            ),
        )

        flask.current_app.logger.debug(query_str)
        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=partition_key_value,
        )

        return result.next()

    def find_all(
        self,
        event_context: EventContext,
        conditions: dict = None,
        custom_sql_conditions: List[str] = None,
        date_range: dict = None,
        **kwargs,
    ):
        conditions = conditions if conditions else {}
        custom_sql_conditions = (
            custom_sql_conditions if custom_sql_conditions else []
        )
        date_range = date_range if date_range else {}

        custom_sql_conditions.append(
            self.create_sql_date_range_filter(date_range)
        )

        custom_params = self.generate_params(date_range)
        time_entries = CosmosDBRepository.find_all(
            self,
            event_context=event_context,
            conditions=conditions,
            custom_sql_conditions=custom_sql_conditions,
            custom_params=custom_params,
            max_count=kwargs.get("max_count", None),
            offset=kwargs.get("offset", 0),
        )

        if time_entries:
            custom_conditions = create_in_condition(time_entries, "project_id")
            custom_conditions_activity = create_in_condition(
                time_entries, "activity_id"
            )

            project_dao = projects_model.create_dao()
            projects = project_dao.get_all(
                custom_sql_conditions=[custom_conditions],
                visible_only=False,
                max_count=kwargs.get("max_count", None),
            )

            add_project_info_to_time_entries(time_entries, projects)

            activity_dao = activities_model.create_dao()
            activities = activity_dao.get_all(
                custom_sql_conditions=[custom_conditions_activity],
                visible_only=False,
                max_count=kwargs.get("max_count", None),
            )
            add_activity_name_to_time_entries(time_entries, activities)

            users = AzureConnection().users()
            add_user_email_to_time_entries(time_entries, users)
        elif not time_entries and len(conditions) > 1:
            abort(HTTPStatus.NOT_FOUND, "Time entry not found")
        return time_entries

    def find_all_v2(
        self,
        event_context: EventContext,
        owner_id_list: List[str],
        date_range: tuple = None,
        fields: dict = None,
        limit: int = None,
        offset: int = 0,
        visible_only=True,
        mapper: Callable = None,
    ):
        limit = self.get_page_size_or(limit)
        partition_key_value = self.find_partition_key_value(event_context)
        query_builder = (
            TimeEntryQueryBuilder()
            .add_sql_date_range_condition(date_range)
            .add_sql_in_condition(owner_id_list)
            .add_sql_where_equal_condition(fields)
            .add_sql_limit_condition(limit)
            .add_sql_offset_condition(offset)
            .build()
        )

        query_str = query_builder.get_query()
        params = query_builder.get_parameters()

        result = self.container.query_items(
            query=query_str,
            parameters=params,
            partition_key=partition_key_value,
        )
        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

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
        params = [
            {"name": "@start_date", "value": start_date},
            {"name": "@end_date", "value": end_date or current_datetime_str()},
            {"name": "@ignore_id", "value": ignore_id},
        ]
        params.extend(self.generate_params(conditions))
        result = self.container.query_items(
            query="""
            SELECT * FROM c
            WHERE (((c.start_date BETWEEN @start_date AND @end_date)
                  OR (c.end_date BETWEEN @start_date AND @end_date))
                  OR ((@start_date BETWEEN c.start_date AND c.end_date)
                  OR (@end_date BETWEEN c.start_date AND c.end_date)))
                  AND c.start_date!= @end_date
                  AND c.end_date!= @start_date
            {conditions_clause}
            {ignore_id_condition}
            {visibility_condition}
            {order_clause}
            """.format(
                ignore_id_condition=self.create_sql_ignore_id_condition(
                    ignore_id
                ),
                visibility_condition=self.create_sql_condition_for_visibility(
                    visible_only
                ),
                conditions_clause=self.create_sql_where_conditions(conditions),
                order_clause=self.create_sql_order_clause(),
            ),
            parameters=params,
            partition_key=tenant_id,
        )

        function_mapper = self.get_mapper_or_dict(mapper)
        return list(map(function_mapper, result))

    def find_running(
        self, tenant_id: str, owner_id: str, mapper: Callable = None
    ):
        conditions = {
            "owner_id": owner_id,
            "tenant_id": tenant_id,
        }
        result = self.container.query_items(
            query="""
            SELECT * from c
            WHERE (NOT IS_DEFINED(c.end_date) OR c.end_date = null)
            {conditions_clause}
            {visibility_condition}
            OFFSET 0 LIMIT 1
            """.format(
                visibility_condition=self.create_sql_condition_for_visibility(
                    True
                ),
                conditions_clause=self.create_sql_where_conditions(conditions),
            ),
            parameters=self.generate_params(conditions),
            partition_key=tenant_id,
            max_item_count=1,
        )

        function_mapper = self.get_mapper_or_dict(mapper)
        return function_mapper(next(result))

    def validate_data(self, data, event_context: EventContext):
        start_date = data.get('start_date')

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

        collision = self.find_interception_with_date_range(
            start_date=start_date,
            end_date=data.get('end_date'),
            owner_id=event_context.user_id,
            tenant_id=event_context.tenant_id,
            ignore_id=data.get('id'),
        )
        if len(collision) > 0:
            raise CustomError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                description="There is another time entry in that date range",
            )
