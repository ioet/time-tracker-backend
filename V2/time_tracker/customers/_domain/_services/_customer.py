import typing

from time_tracker.customers._domain import Customer, CustomersDao


class CustomerService:

    def __init__(self, customer_dao: CustomersDao):
        self.customer_dao = customer_dao

    def create(self, data: Customer) -> Customer:
        return self.customer_dao.create(data)

    # def update(self, data: Customer) -> Customer:
    #     return self.customer_dao.update(data)

    # def get_by_id(self, id: int) -> Customer:
    #     return self.customer_dao.get_by_id(id)

    # def get_all(self) -> typing.List[Customer]:
    #     return self.customer_dao.get_all()

    # def delete(self, id: int) -> Customer:
    #     return self.customer_dao.delete(id)
