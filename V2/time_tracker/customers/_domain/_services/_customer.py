from time_tracker.customers._domain import Customer, CustomersDao


class CustomerService:

    def __init__(self, customer_dao: CustomersDao):
        self.customer_dao = customer_dao

    def create(self, data: Customer) -> Customer:
        return self.customer_dao.create(data)
