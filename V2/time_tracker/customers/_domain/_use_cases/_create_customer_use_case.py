from time_tracker.customers._domain import Customer, CustomerService


class CreateCustomerUseCase:

    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service

    def create_customer(self, data: Customer) -> Customer:
        return self.customer_service.create(data)
