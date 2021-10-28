from time_entries._domain import ActivitiesDao, Activity
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

    def delete(self, activity_id: str) -> Activity:
        activity = self.get_by_id(activity_id)
        if activity:
            activity_deleted = {**activity.__dict__, 'status': 'inactive'}
            activities_updated = list(
                map(
                    lambda activity: activity
                    if activity.get('id') != activity_id
                    else activity_deleted,
                    self.__get_activities_from_file(),
                )
            )

            try:
                file = open(self.json_data_file_path, 'w')
                json.dump(activities_updated, file)
                file.close()

                return self.__create_activity_dto(activity_deleted)

            except FileNotFoundError:
                return None

        else:
            return None

    def update(self, activity_id: str, new_activity: dict) -> Activity:
        activity = self.get_by_id(activity_id)
        if not activity:
            return None

        new_activity = {**activity.__dict__, **new_activity}

        activities_updated = list(
            map(
                lambda activity: activity
                if activity.get('id') != activity_id
                else new_activity,
                self.__get_activities_from_file(),
            )
        )

        try:
            file = open(self.json_data_file_path, 'w')
            json.dump(activities_updated, file)
            file.close()

            return self.__create_activity_dto(new_activity)

        except FileNotFoundError:
            return None

    def create_activity(self, activity_data: dict) -> Activity:
        activities = self.__get_activities_from_file()
        activities.append(activity_data)

        try:
            with open(self.json_data_file_path, 'w') as outfile:
                json.dump(activities, outfile)

            return self.__create_activity_dto(activity_data)
        except FileNotFoundError:
            print("Can not create activity")


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
