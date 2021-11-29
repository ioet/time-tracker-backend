from time_tracker.customers._domain import Customer, CustomerService


class DeleteCustomerUseCase:

    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service

    def delete_customer(self, id: int) -> Customer:
        return self.customer_service.delete(id)
