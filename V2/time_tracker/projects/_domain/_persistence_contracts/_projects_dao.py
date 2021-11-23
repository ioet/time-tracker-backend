import abc

from .. import Project


class ProjectsDao(abc.ABC):
    @abc.abstractmethod
    def create(self, time_entry_data: Project) -> Project:
        pass

    @abc.abstractmethod
    def get_all(self) -> Project:
        pass

    @abc.abstractmethod
    def get_by_id(self, id: int) -> Project:
        pass

    @abc.abstractmethod
    def update(self, id: int, name: str, description: str, customer_id: int, status: int) -> Project:
        pass

    @abc.abstractmethod
    def delete(self, id: int) -> Project:
        pass
