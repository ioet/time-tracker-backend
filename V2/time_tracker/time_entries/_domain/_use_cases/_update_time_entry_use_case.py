from time_tracker.time_entries._domain import TimeEntryService, TimeEntry


class UpdateTimeEntryUseCase:
    def __init__(self, time_entry_service: TimeEntryService):
        self.time_entry_service = time_entry_service

    def update_time_entry(
        self, time_entry_id: int, new_time_entry: dict
    ) -> TimeEntry:
        return self.time_entry_service.update(time_entry_id, new_time_entry)
