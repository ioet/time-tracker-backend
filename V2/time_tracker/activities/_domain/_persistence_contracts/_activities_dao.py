from time_tracker.activities._domain import Activity
import abc
import typing


class ActivitiesDao(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: int) -> Activity:
        pass

    @abc.abstractmethod
    def get_all(self) -> typing.List[Activity]:
        pass

    @abc.abstractmethod
    def delete(self, id: int) -> Activity:
        pass

    @abc.abstractmethod
    def update(self, id: int, name: str, description: str, status: int, deleted: bool) -> Activity:
        pass

    @abc.abstractmethod
    def create(self, activity_data: Activity) -> Activity:
        pass
