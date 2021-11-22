import typing

from time_tracker.customers._domain import Customer, CustomerService


class GetAllCustomerUseCase:

    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service

    def get_all_customer(self) -> typing.List[Customer]:
        return self.customer_service.get_all()
