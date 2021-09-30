from V2.source.daos.activities_dao import ActivitiesDao
from V2.source.dtos.activity import Activity
import json
import typing


class ActivitiesJsonDao(ActivitiesDao):
    def __init__(self, json_data_file_path: str):
        self.json_data_file_path = json_data_file_path
        self.activity_keys = Activity.__dataclass_fields__.keys()

    def get_by_id(self, activity_id: str) -> Activity:
        activities_grouped_by_id = {
            activity.get('id'): activity
            for activity in self.__get_activities_from_file()
        }
        activity = activities_grouped_by_id.get(activity_id)
        activity_dto = (
            self.__create_activity_dto(activity) if activity else None
        )

        return activity_dto

    def get_all(self) -> typing.List[Activity]:
        all_activities = self.__get_activities_from_file()
        activity_dtos = [
            self.__create_activity_dto(activity) for activity in all_activities
        ]

        return activity_dtos

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
        activity_dto = Activity(**activity)
        return activity_dto
