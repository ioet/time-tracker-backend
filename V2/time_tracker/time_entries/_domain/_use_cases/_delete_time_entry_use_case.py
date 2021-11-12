from time_tracker.time_entries._domain import TimeEntry, TimeEntryService


class DeleteTimeEntryUseCase:

    def __init__(self, time_entry_service: TimeEntryService):
        self.time_entry_service = time_entry_service

    def delete_time_entry(self, id: int) -> TimeEntry:
        return self.time_entry_service.delete(id)
