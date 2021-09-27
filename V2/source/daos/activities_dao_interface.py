from V2.source.dtos.activity import ActivityDto
import abc


class ActivitiesDaoInterface(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id: str) -> ActivityDto:
        pass

    @abc.abstractmethod
    def get_all(self) -> list:
        pass
