from time_entries._domain import ActivitiesDao, Activity
import typing


class ActivityService:
    def __init__(self, activities_dao: ActivitiesDao):
        self.activities_dao = activities_dao

    def get_by_id(self, activity_id: str) -> Activity:
        return self.activities_dao.get_by_id(activity_id)

    def get_all(self) -> typing.List[Activity]:
        return self.activities_dao.get_all()

    def delete(self, activity_id: str) -> Activity:
        return self.activities_dao.delete(activity_id)

    def update(self, activity_id: str, new_activity: dict) -> Activity:
        return self.activities_dao.update(activity_id, new_activity)

    def create_activity(self, activity_data: dict) -> Activity:
        return self.activities_dao.create_activity(activity_data)
