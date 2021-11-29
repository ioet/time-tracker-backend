from http import HTTPStatus
import json

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB


def get_customers(req: func.HttpRequest) -> func.HttpResponse:
    customer_id = req.route_params.get('id')
    status_code = HTTPStatus.OK

    try:
        if customer_id:
            response = _get_by_id(int(customer_id))
            if response == b'This customer does not exist':
                status_code = HTTPStatus.NOT_FOUND
        else:
            response = _get_all()

        return func.HttpResponse(
            body=response, status_code=status_code, mimetype="application/json"
        )
    except ValueError:
        return func.HttpResponse(
            body=b"The id has an invalid format", status_code=HTTPStatus.BAD_REQUEST, mimetype="application/json"
        )


def _get_by_id(customer_id: int) -> str:
    customer_use_case = _domain._use_cases.GetByIdCustomerUseCase(
        _create_customer_service(DB())
    )
    customer = customer_use_case.get_customer_by_id(customer_id)

    return json.dumps(customer.__dict__) if customer else b'This customer does not exist'


def _get_all() -> str:
    customer_sql = _domain._use_cases.GetAllCustomerUseCase(
        _create_customer_service(DB())
    )
    return json.dumps(
        [
            customer.__dict__
            for customer in customer_sql.get_all_customer()
        ]
    )


def _create_customer_service(db: DB) -> _domain.CustomerService:
    customer_sql = _infrastructure.CustomersSQLDao(db)
    return _domain.CustomerService(customer_sql)
