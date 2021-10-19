from time_entries._domain import ActivityService, Activity


class GetActivityUseCase:
    def __init__(self, activity_service: ActivityService):
        self.activity_service = activity_service

    def get_activity_by_id(self, id: str) -> Activity:
        return self.activity_service.get_by_id(id)
