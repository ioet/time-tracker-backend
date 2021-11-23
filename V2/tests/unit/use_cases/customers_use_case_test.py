from pytest_mock import MockFixture

from time_tracker.customers._domain import _use_cases


def test__create_customer_function__uses_the_customer_service__to_create_a_customer(
    mocker: MockFixture, customer_factory
):
    expected_customer = mocker.Mock()
    customer_service = mocker.Mock(
        create=mocker.Mock(return_value=expected_customer)
    )

    customer_use_case = _use_cases.CreateCustomerUseCase(customer_service)
    new_customer = customer_use_case.create_customer(customer_factory())

    assert customer_service.create.called
    assert expected_customer == new_customer
