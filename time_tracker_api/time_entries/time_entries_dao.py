import abc
from commons.data_access_layer.cosmos_db import (
    CosmosDBDao,
    CustomError,
)
from utils.extend_model import (
    add_project_info_to_time_entries,
    add_activity_name_to_time_entries,
    create_list_from_str,
)
from utils.time import (
    datetime_str,
    str_to_datetime,
    get_current_year,
    get_current_month,
    get_date_range_of_month,
    current_datetime_str,
)
from flask_restplus import abort
from flask_restplus._http import HTTPStatus
from time_tracker_api.activities import activities_model

from time_tracker_api.projects import projects_model
from utils import worked_time
from datetime import timedelta
from time_tracker_api.time_entries.time_entries_repository import (
    TimeEntryCosmosDBRepository,
)
from time_tracker_api.database import CRUDDao, APICosmosDBDao
from time_tracker_api.security import current_user_id
from utils.azure_users import AzureConnection


class TimeEntriesDao(CRUDDao):
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
        if data.owner_id is not None and data.owner_id != current_user_id():
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

    def get_owner_ids(self, is_admin: bool, conditions: dict = None):
        custom_query = []
        if "user_id" in conditions:
            if is_admin:
                conditions.pop("owner_id")
                custom_query = (
                    []
                    if conditions.get("user_id") == "*"
                    else create_list_from_str(conditions.get("user_id"))
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
        is_complete_query = conditions.get("user_id") == '*'
        owner_ids = self.get_owner_ids(
            is_admin=event_ctx.is_admin,
            conditions=conditions,
        )
        date_range = self.handle_date_filter_args(args=conditions)
        limit = conditions.pop("limit", None)
        azure_connection = AzureConnection()
        current_user_is_tester = azure_connection.is_test_user(
            event_ctx.user_id
        )

        test_user_ids = (
            azure_connection.get_test_user_ids()
            if not current_user_is_tester and is_complete_query
            else None
        )

        time_entries_list = self.repository.find_all(
            conditions=conditions,
            test_user_ids=test_user_ids,
            owner_ids=owner_ids,
            date_range=date_range,
            max_count=limit,
            event_context=event_ctx,
        )

        return time_entries_list

    def get_latest_entries(self, conditions: dict = None):
        """
        Get the latest entries without taking into account a data range.
        It would only be necessary to pass the number of last entries that
        you need, this parameter must be passed by the conditions.
        The default value for the entries amount is 20.
        """
        conditions = conditions if conditions else {}

        default_entries_amount = 20
        event_context = self.create_event_context('read_many')
        conditions.update({'owner_id': event_context.user_id})
        entries_amount = conditions.pop("limit", default_entries_amount)
        time_entries = self.repository.find_all(
            conditions=conditions,
            max_count=entries_amount,
            event_context=event_context,
        )

        return time_entries

    def get_lastest_entries_by_project(
        self, conditions: dict = None, **kwargs
    ) -> list:
        event_ctx = self.create_event_context("read-many")
        conditions.update({"owner_id": event_ctx.user_id})

        date_range = self.handle_date_filter_args(args=conditions)

        project_dao = projects_model.create_dao()
        projects = project_dao.get_all()
        projects_ids = [project.id for project in projects]

        activity_dao = activities_model.create_dao()
        activities = activity_dao.get_all(
            visible_only=False,
        )

        result = []
        for id_project in projects_ids:
            conditions.update({"project_id": id_project})

            latest = self.repository.find_all_entries(
                event_ctx,
                conditions=conditions,
                date_range=date_range,
                max_count=1,
            )

            if len(latest) > 0:
                self.append = result.append(latest[0])

        add_activity_name_to_time_entries(result, activities)
        add_project_info_to_time_entries(result, projects)

        return result

    def get_all_paginated(self, conditions: dict = None, **kwargs) -> list:
        get_all_conditions = dict(conditions)
        get_all_conditions.pop("length")
        get_all_conditions.pop("start")
        event_ctx = self.create_event_context("read-many")
        get_all_conditions.update({"owner_id": event_ctx.user_id})
        owner_ids = self.get_owner_ids(
            is_admin=event_ctx.is_admin,
            conditions=get_all_conditions,
        )
        date_range = self.handle_date_filter_args(args=get_all_conditions)
        records_total = self.repository.count(
            event_ctx,
            conditions=get_all_conditions,
            owner_ids=owner_ids,
            date_range=date_range,
        )
        conditions.update({"owner_id": event_ctx.user_id})
        owner_ids = self.get_owner_ids(
            is_admin=event_ctx.is_admin,
            conditions=conditions,
        )
        date_range = self.handle_date_filter_args(args=conditions)
        length = conditions.get("length", None)
        conditions.pop("length", None)
        start = conditions.get("start", None)
        conditions.pop("start", None)

        time_entries = self.repository.find_all(
            event_context=event_ctx,
            conditions=conditions,
            owner_ids=owner_ids,
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
        data['owner_id'] = event_ctx.user_id
        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)

        if data.get('update_last_entry_if_overlap', None):
            self.repository.update_last_entry(
                data.get('owner_id'),
                data.get('start_date'),
                data.get('id'),
                event_ctx,
            )

        return self.repository.partial_update(
            id,
            data,
            event_ctx,
        )

    def stop(self, id):
        event_ctx = self.create_event_context("update", "Stop time entry")

        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)
        self.check_time_entry_is_not_stopped(time_entry)

        return self.repository.partial_update(
            id,
            {'end_date': current_datetime_str()},
            event_ctx,
        )

    def restart(self, id):
        event_ctx = self.create_event_context("update", "Restart time entry")

        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)
        self.check_time_entry_is_not_started(time_entry)

        return self.repository.partial_update(
            id,
            {'end_date': None},
            event_ctx,
        )

    def delete(self, id):
        event_ctx = self.create_event_context("delete")
        time_entry = self.repository.find(id, event_ctx)
        self.check_whether_current_user_owns_item(time_entry)
        self.repository.delete(
            id,
            event_ctx,
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
