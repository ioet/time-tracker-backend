from time_tracker.time_entries._domain import TimeEntry, TimeEntryService


class CreateTimeEntryUseCase:

    def __init__(self, time_entry_service: TimeEntryService):
        self.time_entry_service = time_entry_service

    def create_time_entry(self, time_entry_data: TimeEntry) -> TimeEntry:
        return self.time_entry_service.create(time_entry_data.__dict__)
