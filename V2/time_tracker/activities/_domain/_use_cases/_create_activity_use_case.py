from time_tracker.activities._domain import ActivityService, Activity
import typing


class CreateActivityUseCase:
    def __init__(self, activity_service: ActivityService):
        self.activity_service = activity_service

    def create_activity(self, activity_data: dict ) -> Activity:
        return self.activity_service.create(activity_data)

