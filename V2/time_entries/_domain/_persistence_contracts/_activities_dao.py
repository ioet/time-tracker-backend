from time_entries._domain import Activity
import abc
import typing


class ActivitiesDao(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: str) -> Activity:
        pass

    @abc.abstractmethod
    def get_all(self) -> typing.List[Activity]:
        pass

    @abc.abstractmethod
    def delete(self, id: str) -> Activity:
        pass

    @abc.abstractmethod
    def update(self, id: str, new_activity: dict) -> Activity:
        pass

    @abc.abstractmethod
    def create_activity(self, activity_data: dict) -> Activity:
        pass

    @abc.abstractmethod
    def delete(self, id: str) -> Activity:
        pass
