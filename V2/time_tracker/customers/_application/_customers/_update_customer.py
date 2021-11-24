import dataclasses
import json
import typing

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB


def update_customer(req: func.HttpRequest) -> func.HttpResponse:
    try:
        database = DB()
        customer_id = int(req.route_params.get('id'))
        customer_dao = _infrastructure.CustomersSQLDao(database)
        customer_service = _domain.CustomerService(customer_dao)
        use_case = _domain._use_cases.UpdateCustomerUseCase(customer_service)

        customer_data = req.get_json()
        customer_is_invalid = _validate_customer(customer_data)
        if customer_is_invalid:
            raise ValueError

        customer_to_update = _domain.Customer(
            **{field.name: customer_data.get(field.name) for field in dataclasses.fields(_domain.Customer)}
        )
        updated_customer = use_case.update_customer(customer_id, customer_to_update)

        if updated_customer:
            body = json.dumps(updated_customer.__dict__)
            status_code = 200
        else:
            body = b'This customer does not exist'
            status_code = 409

        return func.HttpResponse(
            body=body,
            status_code=status_code,
            mimetype="application/json"
        )
    except ValueError:
        return func.HttpResponse(
            body=b'Invalid format or structure of the attributes of the customer',
            status_code=400,
            mimetype="application/json"
        )


def _validate_customer(customer_data: dict) -> typing.List[str]:
    return [field.name for field in dataclasses.fields(_domain.Customer)
            if field.name not in customer_data]
