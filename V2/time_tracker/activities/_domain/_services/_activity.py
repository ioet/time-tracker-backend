from time_tracker.activities._domain import ActivitiesDao, Activity
import typing


class ActivityService:
    def __init__(self, activities_dao: ActivitiesDao):
        self.activities_dao = activities_dao

    def get_by_id(self, activity_id: int) -> Activity:
        return self.activities_dao.get_by_id(activity_id)

    def get_all(self) -> typing.List[Activity]:
        return self.activities_dao.get_all()

    def delete(self, activity_id: int) -> Activity:
        return self.activities_dao.delete(activity_id)

    def update(self, activity_id: int, name: str, description: str, status: int, deleted: bool) -> Activity:
        return self.activities_dao.update(activity_id, name, description, status, deleted)

    def create(self, activity_data: Activity) -> Activity:
        return self.activities_dao.create(activity_data)
