import abc
import typing

from time_tracker.time_entries._domain import TimeEntry


class TimeEntriesDao(abc.ABC):
    @abc.abstractmethod
    def create(self, time_entry_data: TimeEntry) -> TimeEntry:
        pass

    @abc.abstractmethod
    def delete(self, id: int) -> TimeEntry:
        pass

    @abc.abstractmethod
    def update(self, id: int, new_time_entry: dict) -> TimeEntry:
        pass

    @abc.abstractmethod
    def get_by_id(self, id: int) -> TimeEntry:
        pass

    @abc.abstractmethod
    def get_all(self) -> typing.List[TimeEntry]:
        pass

    @abc.abstractmethod
    def get_latest_entries(self, owner_id: int, limit: int) -> typing.List[TimeEntry]:
        pass
