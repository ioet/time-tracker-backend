import abc
import typing

from .. import Project


class ProjectsDao(abc.ABC):
    @abc.abstractmethod
    def create(self, time_entry_data: Project) -> Project:
        pass

    @abc.abstractmethod
    def get_all(self) -> typing.List[Project]:
        pass

    @abc.abstractmethod
    def get_by_id(self, id: int) -> Project:
        pass

    @abc.abstractmethod
    def update(self, id: int, project_data: dict) -> Project:
        pass

    @abc.abstractmethod
    def delete(self, id: int) -> Project:
        pass

    @abc.abstractmethod
    def get_latest(self, owner_id: int) -> typing.List[Project]:
        pass
