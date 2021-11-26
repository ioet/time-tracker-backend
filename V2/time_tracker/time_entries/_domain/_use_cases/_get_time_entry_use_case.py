import typing

from time_tracker.time_entries._domain import TimeEntryService, TimeEntry


class GetTimeEntriesUseCase:
    def __init__(self, time_entry_service: TimeEntryService):
        self.time_entry_service = time_entry_service

    def get_time_entries(self) -> typing.List[TimeEntry]:
        return self.time_entry_service.get_all()
