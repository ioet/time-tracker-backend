from time_tracker.customers._domain import Customer, CustomerService


class UpdateCustomerUseCase:

    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service

    def update_customer(self, id: int, data: Customer) -> Customer:
        return self.customer_service.update(id, data)
