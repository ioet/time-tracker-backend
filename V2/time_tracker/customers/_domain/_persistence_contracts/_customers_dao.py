import abc
import typing

from time_tracker.customers._domain import Customer


class CustomersDao(abc.ABC):
    @abc.abstractmethod
    def create(self, data: Customer) -> Customer:
        pass

    @abc.abstractmethod
    def update(self, id: int, data: Customer) -> Customer:
        pass

    @abc.abstractmethod
    def get_by_id(self, id: int) -> Customer:
        pass

    @abc.abstractmethod
    def get_all(self) -> typing.List[Customer]:
        pass

    @abc.abstractmethod
    def delete(self, id: int) -> Customer:
        pass
