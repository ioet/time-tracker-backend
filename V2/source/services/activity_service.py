from V2.source.daos.activities_dao_interface import ActivitiesDaoInterface
from V2.source.dtos.activity import ActivityDto


class ActivityService:

    activities_dao: ActivitiesDaoInterface

    def __init__(self, activities_dao: ActivitiesDaoInterface):
        self.activities_dao = activities_dao

    def get_by_id(self, id: str) -> ActivityDto:
        activity_dto = self.activities_dao.get_by_id(id)
        return activity_dto

    def get_all(self) -> list:
        list_activities = self.activities_dao.get_all()
        return list_activities
