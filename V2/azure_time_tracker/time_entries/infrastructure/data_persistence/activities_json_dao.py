from time_entries.domain import ActivitiesDao
from time_entries.domain import Activity
import dataclasses
import json
import typing


class ActivitiesJsonDao(ActivitiesDao):
    def __init__(self, json_data_file_path: str):
        self.json_data_file_path = json_data_file_path
        self.activity_keys = [
            field.name for field in dataclasses.fields(Activity)
        ]

    def get_by_id(self, activity_id: str) -> Activity:
        activity = {
            activity.get('id'): activity
            for activity in self.__get_activities_from_file()
        }.get(activity_id)

        return self.__create_activity_dto(activity) if activity else None

    def get_all(self) -> typing.List[Activity]:
        return [
            self.__create_activity_dto(activity)
            for activity in self.__get_activities_from_file()
        ]

    def __get_activities_from_file(self) -> typing.List[dict]:
        try:
            file = open(self.json_data_file_path)
            activities = json.load(file)
            file.close()

            return activities

        except FileNotFoundError:
            return []

    def __create_activity_dto(self, activity: dict) -> Activity:
        activity = {key: activity.get(key) for key in self.activity_keys}
        return Activity(**activity)
