import abc

from time_tracker.time_entries._domain import TimeEntry

class TimeEntriesDao(abc.ABC):
    def create(self, time_entry_data: dict) -> TimeEntry:
        pass