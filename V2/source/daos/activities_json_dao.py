from V2.source.daos.activities_dao_interface import ActivitiesDaoInterface
from V2.source.dtos.activity import ActivityDto
from http import HTTPStatus
import json


class ActivitiesJsonDao(ActivitiesDaoInterface):
    def __init__(self, json_data_file_path):
        self.json_data_file_path = json_data_file_path
        self.activity_keys = ActivityDto.__dataclass_fields__.keys()

    def get_by_id(self, id):
        try:
            file = open(self.json_data_file_path)
            activities = json.load(file)
            file.close()

        except FileNotFoundError:
            return HTTPStatus.NOT_FOUND

        activity = next(
            (activity for activity in activities if activity.get('id') == id),
            None,
        )

        if activity == None:
            return HTTPStatus.NOT_FOUND

        activity = {key: activity.get(key) for key in self.activity_keys}
        activity_dto = ActivityDto(**activity)

        return activity_dto

    def get_all(self):
        try:
            file = open(self.json_data_file_path)
            activities = json.load(file)
            file.close()

        except FileNotFoundError:
            return HTTPStatus.NOT_FOUND

        list_activities = []

        for activity in activities:
            activity = {key: activity.get(key) for key in self.activity_keys}
            activity_dto = ActivityDto(**activity)
            list_activities.append(activity_dto)

        return list_activities
