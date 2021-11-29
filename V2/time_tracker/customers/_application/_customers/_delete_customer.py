import json
from http import HTTPStatus

import azure.functions as func

from ... import _domain
from ... import _infrastructure
from time_tracker._infrastructure import DB

DATATYPE = "application/json"


def delete_customer(req: func.HttpRequest) -> func.HttpResponse:
    customer_dao = _infrastructure.CustomersSQLDao(DB())
    customer_service = _domain.CustomerService(customer_dao)
    use_case = _domain._use_cases.DeleteCustomerUseCase(customer_service)

    try:
        customer_id = int(req.route_params.get("id"))
        deleted_customer = use_case.delete_customer(customer_id)
        if not deleted_customer:
            return func.HttpResponse(
                body="Not found",
                status_code=HTTPStatus.NOT_FOUND,
                mimetype=DATATYPE
            )

        return func.HttpResponse(
            body=json.dumps(deleted_customer.__dict__, default=str),
            status_code=HTTPStatus.OK,
            mimetype=DATATYPE,
        )

    except ValueError:
        return func.HttpResponse(
            body=b"Invalid Format ID",
            status_code=HTTPStatus.BAD_REQUEST,
            mimetype=DATATYPE
        )
