import abc

from time_tracker.customers._domain import Customer


class CustomersDao(abc.ABC):
    @abc.abstractmethod
    def create(self, data: Customer) -> Customer:
        pass
