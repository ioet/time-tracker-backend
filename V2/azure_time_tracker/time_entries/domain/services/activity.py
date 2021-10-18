from time_entries.domain import ActivitiesDao
from time_entries.domain import Activity
import typing


class ActivityService:
    def __init__(self, activities_dao: ActivitiesDao):
        self.activities_dao = activities_dao

    def get_by_id(self, activity_id: str) -> Activity:
        return self.activities_dao.get_by_id(activity_id)

    def get_all(self) -> typing.List[Activity]:
        return self.activities_dao.get_all()
