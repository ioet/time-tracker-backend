from time_entries.domain import Activity
import abc
import typing


class ActivitiesDao(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: str) -> Activity:
        pass

    @abc.abstractmethod
    def get_all(self) -> typing.List[Activity]:
        pass
