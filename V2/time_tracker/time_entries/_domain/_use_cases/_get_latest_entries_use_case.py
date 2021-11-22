from time_tracker.time_entries._domain import TimeEntry, TimeEntryService
import typing


class GetLastestTimeEntryUseCase:

    def __init__(self, time_entry_service: TimeEntryService):
        self.time_entry_service = time_entry_service

    def get_latest_entries(self, owner_id: int, limit: int) -> typing.List[TimeEntry]:
        return self.time_entry_service.get_latest_entries(owner_id, limit)
