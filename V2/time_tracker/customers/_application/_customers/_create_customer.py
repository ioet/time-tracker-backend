import dataclasses
import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB

DEFAULT_FIELDS = ["id", "deleted", "status"]


# TODO: VALIDAR QUE NO EXISTA EL CLIENTE ANTES DE AGREGARLO
def create_customer(req: func.HttpRequest) -> func.HttpResponse:
    try:
        database = DB()
        customer_dao = _infrastructure.CustomersSQLDao(database)
        customer_service = _domain.CustomerService(customer_dao)
        use_case = _domain._use_cases.CreateCustomerUseCase(customer_service)
        customer_data = req.get_json()
        customer_is_valid = _validate_customer(customer_data)
        if not customer_is_valid:
            raise ValueError

        customer_to_create = _domain.Customer(
            **dict.fromkeys(DEFAULT_FIELDS),
            name=customer_data["name"],
            description=customer_data["description"],
        )
        created_customer = use_case.create_customer(customer_to_create)
        if not created_customer:
            return func.HttpResponse(
                body=b'customer could not be created',
                status_code=500,
                mimetype="application/json"
            )

        return func.HttpResponse(
            body=json.dumps(created_customer.__dict__),
            status_code=201,
            mimetype="application/json"
        )
    except ValueError:
        return func.HttpResponse(
            body=b'Invalid format or structure of the attributes of the customer',
            status_code=400,
            mimetype="application/json"
        )


def _validate_customer(customer_data: dict) -> bool:
    if [field.name for field in dataclasses.fields(_domain.Customer)
            if (field.name not in customer_data) and (field.name not in DEFAULT_FIELDS)]:
        return False
    return True
