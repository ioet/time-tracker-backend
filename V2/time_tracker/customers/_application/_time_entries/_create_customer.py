import dataclasses
import json
import typing

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB

DEFAULT_FIELDS = ["id", "deleted", "status"]


def create_customer(req: func.HttpRequest) -> func.HttpResponse:
    database = DB()
    customer_dao = _infrastructure.CustomersSQLDao(database)
    customer_service = _domain.CustomerService(customer_dao)
    use_case = _domain._use_cases.CreateCustomerUseCase(customer_service)

    customer_data = req.get_json()
    validation_errors = _validate_customer(customer_data)
    if validation_errors:
        return func.HttpResponse(
            body=validation_errors, status_code=400, mimetype="application/json"
        )

    customer_to_create = _domain.Customer(
        id=None,
        name=customer_data["name"],
        description=customer_data["description"],
        deleted=False,
        status=-1
    )

    created_customer = use_case.create_customer(customer_to_create)

    if not created_customer:
        return func.HttpResponse(
            body=json.dumps({'error': 'customer could not be created'}),
            status_code=500,
            mimetype="application/json"
        )

    return func.HttpResponse(
        body=json.dumps(created_customer.__dict__),
        status_code=201,
        mimetype="application/json"
    )


def _validate_customer(customer_data: dict) -> typing.List[str]:
    customer_fields = [field.name for field in dataclasses.fields(_domain.Customer) 
                        if field.name not in DEFAULT_FIELDS]
    if [field for field in customer_fields if field not in customer_data]:
        return b'Invalid format or structure of the attributes of the customer'
    return []
