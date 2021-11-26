from time_tracker.time_entries._domain import TimeEntryService, TimeEntry


class GetTimeEntryUseCase:
    def __init__(self, time_entry_service: TimeEntryService):
        self.time_entry_service = time_entry_service

    def get_time_entry_by_id(self, id: int) -> TimeEntry:
        return self.time_entry_service.get_by_id(id)
