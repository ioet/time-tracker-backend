from time_entries._domain import ActivityService, Activity


class DeleteActivityUseCase:
    def __init__(self, activity_service: ActivityService):
        self.activity_service = activity_service

    def delete_activity(self, id: str) -> Activity:
        return self.activity_service.delete(id)
