from V2.source.services.activity_service import ActivityService
from V2.source.dtos.activity import Activity
import typing


class GetActivitiesUseCase:
    def __init__(self, activity_service: ActivityService):
        self.activity_service = activity_service

    def get_activities(self) -> typing.List[Activity]:
        return self.activity_service.get_all()
