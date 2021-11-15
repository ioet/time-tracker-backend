from time_tracker.activities._domain import ActivityService, Activity


class UpdateActivityUseCase:
    def __init__(self, activity_service: ActivityService):
        self.activity_service = activity_service

    def update_activity(
        self, activity_id: int, name: str, description: str, status: int, deleted: bool
    ) -> Activity:
        return self.activity_service.update(activity_id, name, description, status, deleted)
