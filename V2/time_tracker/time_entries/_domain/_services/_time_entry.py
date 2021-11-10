from time_tracker.time_entries._domain import TimeEntry, TimeEntriesDao

class TimeEntryService:
  
  def __init__(self, time_entry_dao: TimeEntriesDao):
    self.time_entry_dao = time_entry_dao

  def create(self, time_entry_data: dict) -> TimeEntry:
    return self.time_entry_dao.create(time_entry_data)