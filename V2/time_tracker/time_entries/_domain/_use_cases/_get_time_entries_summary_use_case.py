import typing

from time_tracker.time_entries._domain import TimeEntry, TimeEntryService


class GetTimeEntriesSummaryUseCase:

    def __init__(self, time_entry_service: TimeEntryService):
        self.time_entry_service = time_entry_service

    def get_time_entries_summary(self, owner_id: int, start_date: str, end_date: str) -> typing.List[TimeEntry]:
        return self.time_entry_service.get_time_entries_summary(owner_id, start_date, end_date)
