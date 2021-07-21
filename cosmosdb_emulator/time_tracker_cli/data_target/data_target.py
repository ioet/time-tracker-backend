from abc import ABC, abstractmethod


class DataTarget(ABC):
    @abstractmethod
    def save(self, entities: dict):
        pass

    @abstractmethod
    def delete(self, entities: set):
        pass
