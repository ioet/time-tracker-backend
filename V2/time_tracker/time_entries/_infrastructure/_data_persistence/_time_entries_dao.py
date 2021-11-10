import json
import dataclasses
import typing

from time_tracker.time_entries._domain import TimeEntriesDao, TimeEntry

class TimeEntriesJsonDao(TimeEntriesDao):
    
  def __init__(self, json_data_file_path: str):
      self.json_data_file_path = json_data_file_path
      self.time_entry_key = [field.name for field in dataclasses.fields(TimeEntry)]

  def create(self, time_entry_data: dict) -> TimeEntry:
        time_entries = self.__get_time_entries_from_file()
        time_entries.append(time_entry_data)

        try:
            with open(self.json_data_file_path, 'w') as outfile:
                json.dump(time_entries, outfile)

            return self.__create_time_entry_dto(time_entry_data)
        except FileNotFoundError:
            print("Can not create activity")

  def __get_time_entries_from_file(self) -> typing.List[dict]:
    try:
        file = open(self.json_data_file_path)
        time_entries = json.load(file)
        file.close()

        return time_entries

    except FileNotFoundError:
        return []

  def __create_time_entry_dto(self, time_entry: dict) -> TimeEntry:
        time_entry = {key: time_entry.get(key) for key in self.time_entry_key}
        return TimeEntry(**time_entry)