import abc

from time_tracker.time_entries._domain import TimeEntry


class TimeEntriesDao(abc.ABC):
    @abc.abstractmethod
    def create(self, time_entry_data: TimeEntry) -> TimeEntry:
        pass

    @abc.abstractmethod
    def delete(self, id: int) -> TimeEntry:
        pass
