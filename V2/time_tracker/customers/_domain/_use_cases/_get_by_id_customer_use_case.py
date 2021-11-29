from time_tracker.customers._domain import Customer, CustomerService


class GetByIdCustomerUseCase:

    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service

    def get_customer_by_id(self, id: int) -> Customer:
        return self.customer_service.get_by_id(id)
