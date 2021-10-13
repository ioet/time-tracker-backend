from time_tracker.source.services.activity_service import ActivityService
from time_tracker.source.dtos.activity import Activity


class GetActivityUseCase:
    def __init__(self, activity_service: ActivityService):
        self.activity_service = activity_service

    def get_activity_by_id(self, id: str) -> Activity:
        return self.activity_service.get_by_id(id)
