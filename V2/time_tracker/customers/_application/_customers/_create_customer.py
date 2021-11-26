import dataclasses
import json
import typing
from http import HTTPStatus

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB


def create_customer(req: func.HttpRequest) -> func.HttpResponse:
    try:
        database = DB()
        customer_dao = _infrastructure.CustomersSQLDao(database)
        customer_service = _domain.CustomerService(customer_dao)
        use_case = _domain._use_cases.CreateCustomerUseCase(customer_service)
        customer_data = req.get_json()

        customer_is_invalid = _validate_customer(customer_data)
        if customer_is_invalid:
            raise ValueError

        customer_to_create = _domain.Customer(
            id=None,
            deleted=None,
            status=None,
            name=str(customer_data["name"]).strip(),
            description=str(customer_data["description"]),
        )
        created_customer = use_case.create_customer(customer_to_create)

        if created_customer:
            body = json.dumps(created_customer.__dict__)
            status_code = HTTPStatus.CREATED
        else:
            body = b'This customer already exists'
            status_code = HTTPStatus.CONFLICT

        return func.HttpResponse(
            body=body,
            status_code=status_code,
            mimetype="application/json"
        )
    except ValueError:
        return func.HttpResponse(
            body=b'Invalid format or structure of the attributes of the customer',
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype="application/json"
        )


def _validate_customer(customer_data: dict) -> typing.List[str]:
    return [field.name for field in dataclasses.fields(_domain.Customer)
            if (field.name not in customer_data) and (field.type != typing.Optional[field.type])]
