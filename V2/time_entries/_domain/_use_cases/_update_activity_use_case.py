from time_entries._domain import ActivityService, Activity


class UpdateActivityUseCase:
    def __init__(self, activity_service: ActivityService):
        self.activity_service = activity_service

    def update_activity(
        self, activity_id: str, new_activity: dict
    ) -> Activity:
        return self.activity_service.update(activity_id, new_activity)
