import abc
from flask_restplus import abort
from flask_restplus._http import HTTPStatus

from datetime import timedelta

from commons.data_access_layer.cosmos_db import (
    CosmosDBDao,
    CustomError,
)

from utils.extend_model import (
    create_custom_query_from_str,
)
from utils.time import (
    datetime_str,
    str_to_datetime,
    get_current_year,
    get_current_month,
    get_date_range_of_month,
    current_datetime_str,
)
from utils import worked_time
from time_tracker_api.projects import projects_model
from time_tracker_api.database import CRUDDao, APICosmosDBDao
from time_tracker_api.security import current_user_id
from time_tracker_api.time_entries.time_entries_repository import TimeEntryCosmosDBRepository


class TimeEntriesDao(CRUDDao):
    @staticmethod
    def current_user_id():
        return current_user_id()

    @abc.abstractmethod
    def find_running(self):
        pass

    @abc.abstractmethod
    def stop(self, id: str):
        pass

    @abc.abstractmethod
    def restart(self, id: str):
        pass


class TimeEntriesCosmosDBDao(APICosmosDBDao, TimeEntriesDao):
    def __init__(self, repository):
        CosmosDBDao.__init__(self, repository)

    def check_whether_current_user_owns_item(self, data):
        if (
            data.owner_id is not None
            and data.owner_id != self.current_user_id()
        ):
            raise CustomError(
                HTTPStatus.FORBIDDEN,
                "The current user is not the owner of this time entry",
            )

    def check_time_entry_is_not_stopped(self, data):
        if data.end_date is not None:
            raise CustomError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "The specified time entry is already stopped",
            )

    def check_time_entry_is_not_started(self, data):
        if data.end_date is None:
            raise CustomError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "The specified time entry is already running",
            )

    def build_custom_query(self, is_admin: bool, conditions: dict = None):
        custom_query = []
        if "user_id" in conditions:
            if is_admin:
                conditions.pop("owner_id")
                custom_query = (
                    []
                    if conditions.get("user_id") == "*"
                    else [
                        create_custom_query_from_str(
                            conditions.get("user_id"), "c.owner_id"
                        )
                    ]
                )
                conditions.pop("user_id")
            else:
                abort(
                    HTTPStatus.FORBIDDEN, "You don't have enough permissions."
                )
        return custom_query

    def get_all(self, conditions: dict = None, **kwargs) -> list:
        event_ctx = self.create_event_context("read-many")
        conditions.update({"owner_id": event_ctx.user_id})

        custom_query = self.build_custom_query(
            is_admin=event_ctx.is_admin, conditions=conditions,
        )
        date_range = self.handle_date_filter_args(args=conditions)
        limit = conditions.get("limit", None)
        conditions.pop("limit", None)
        return self.repository.find_all(
            event_ctx,
            conditions=conditions,
            custom_sql_conditions=custom_query,
            date_range=date_range,
            max_count=limit,
        )

    def get_all_paginated(self, conditions: dict = None, **kwargs) -> list:
        get_all_conditions = dict(conditions)
        get_all_conditions.pop("length")
        get_all_conditions.pop("start")
        event_ctx = self.create_event_context("read-many")
        get_all_conditions.update({"owner_id": event_ctx.user_id})
        custom_query = self.build_custom_query(
            is_admin=event_ctx.is_admin, conditions=get_all_conditions,
        )
        date_range = self.handle_date_filter_args(args=get_all_conditions)
        records_total = self.repository.count(
            event_ctx,
            conditions=get_all_conditions,
            custom_sql_conditions=custom_query,
            date_range=date_range,
        )
        conditions.update({"owner_id": event_ctx.user_id})
        custom_query = self.build_custom_query(
            is_admin=event_ctx.is_admin, conditions=conditions,
        )
        date_range = self.handle_date_filter_args(args=conditions)
        length = conditions.get("length", None)
        conditions.pop("length", None)
        start = conditions.get("start", None)
        conditions.pop("start", None)

        time_entries = self.repository.find_all(
            event_ctx,
            conditions=conditions,
            custom_sql_conditions=custom_query,
            date_range=date_range,
            max_count=length,
            offset=start,
        )

        return {
            'records_total': records_total,
            'data': time_entries,
        }

    def get(self, id):
        event_ctx = self.create_event_context("read")

        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)

        project_dao = projects_model.create_dao()
        project = project_dao.get(time_entry.project_id)
        setattr(time_entry, 'project_name', project.name)
        return time_entry

    def create(self, data: dict):
        event_ctx = self.create_event_context("create")
        data['owner_id'] = event_ctx.user_id
        return self.repository.create(data, event_ctx)

    def update(self, id, data: dict, description=None):
        event_ctx = self.create_event_context("update", description)

        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)

        return self.repository.partial_update(id, data, event_ctx,)

    def stop(self, id):
        event_ctx = self.create_event_context("update", "Stop time entry")

        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)
        self.check_time_entry_is_not_stopped(time_entry)

        return self.repository.partial_update(
            id, {'end_date': current_datetime_str()}, event_ctx,
        )

    def restart(self, id):
        event_ctx = self.create_event_context("update", "Restart time entry")

        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)
        self.check_time_entry_is_not_started(time_entry)

        return self.repository.partial_update(
            id, {'end_date': None}, event_ctx,
        )

    def delete(self, id):
        event_ctx = self.create_event_context("delete")
        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)
        self.repository.delete(
            id, event_ctx,
        )

    def find_running(self):
        event_ctx = self.create_event_context("find_running")
        time_entry = self.repository.find_running(
            event_ctx.tenant_id, event_ctx.user_id
        )
        return time_entry

    def get_worked_time(self, args: dict):
        event_ctx = self.create_event_context(
            "read", "Summary of worked time in the current month"
        )

        conditions = {"owner_id": event_ctx.user_id}
        time_entries = self.repository.find_all_entries(
            event_ctx,
            conditions=conditions,
            date_range=worked_time.date_range(),
        )
        return worked_time.summary(
            time_entries, time_offset=args.get('time_offset')
        )

    @staticmethod
    def handle_date_filter_args(args: dict) -> dict:
        if "start_date" and "end_date" in args:
            start_date = str_to_datetime(args.pop('start_date'))
            end_date = str_to_datetime(args.pop('end_date'))
        else:
            month = int(args.pop("month", get_current_month()))
            year = int(args.pop("year", get_current_year()))
            start_date, end_date = get_date_range_of_month(year, month)

        offset_in_minutes = int(args.pop('timezone_offset', 300))
        start_date = start_date + timedelta(minutes=offset_in_minutes)
        end_date = end_date + timedelta(minutes=offset_in_minutes)

        return {
            'start_date': datetime_str(start_date),
            'end_date': datetime_str(end_date),
        }


def create_dao() -> TimeEntriesDao:
    repository = TimeEntryCosmosDBRepository()
    return TimeEntriesCosmosDBDao(repository)
