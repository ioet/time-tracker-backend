from V2.source.daos.activities_dao_interface import ActivitiesDaoInterface
from V2.source.dtos.activity import ActivityDto
from http import HTTPStatus
import json


class ActivitiesJsonDao(ActivitiesDaoInterface):
    def __init__(self, json_data_file_path: str):
        self.json_data_file_path = json_data_file_path
        self.activity_keys = ActivityDto.__dataclass_fields__.keys()

    def get_by_id(self, id: str) -> ActivityDto:
        activities = self.__get_activities_from_file()

        try:
            activity = next(
                (
                    activity
                    for activity in activities
                    if activity.get('id') == id
                )
            )
        except Exception:
            return HTTPStatus.NOT_FOUND

        activity = self.__create_activity_dto(activity)

        return activity

    def get_all(self) -> list:
        activities = self.__get_activities_from_file()
        list_activities = []

        for activity in activities:
            activity = self.__create_activity_dto(activity)
            list_activities.append(activity)

        return list_activities

    def __get_activities_from_file(self) -> list:
        try:
            file = open(self.json_data_file_path)
            activities = json.load(file)
            file.close()

            return activities

        except FileNotFoundError:
            return []

    def __create_activity_dto(self, activity: dict) -> ActivityDto:
        activity = {key: activity.get(key) for key in self.activity_keys}
        activity_dto = ActivityDto(**activity)
        return activity_dto
