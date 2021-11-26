import typing

from time_tracker.time_entries._domain import TimeEntry, TimeEntriesDao


class TimeEntryService:
    def __init__(self, time_entry_dao: TimeEntriesDao):
        self.time_entry_dao = time_entry_dao

    def create(self, time_entry_data: TimeEntry) -> TimeEntry:
        return self.time_entry_dao.create(time_entry_data)

    def delete(self, id: int) -> TimeEntry:
        return self.time_entry_dao.delete(id)

    def update(self, time_entry_id: int, new_time_entry: dict) -> TimeEntry:
        return self.time_entry_dao.update(time_entry_id, new_time_entry)

    def get_by_id(self, id: int) -> TimeEntry:
        return self.time_entry_dao.get_by_id(id)

    def get_all(self) -> typing.List[TimeEntry]:
        return self.time_entry_dao.get_all()
