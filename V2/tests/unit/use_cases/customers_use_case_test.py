from pytest_mock import MockFixture
from faker import Faker

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


def test__delete_customer_function__uses_the_customer_service__to_delete_customer_selected(
    mocker: MockFixture,
):
    expected_customer = mocker.Mock()
    customer_service = mocker.Mock(delete=mocker.Mock(return_value=expected_customer))

    customer_use_case = _use_cases.DeleteCustomerUseCase(customer_service)
    deleted_customer = customer_use_case.delete_customer(Faker().pyint())

    assert customer_service.delete.called
    assert expected_customer == deleted_customer


def test__get_list_customers_function__uses_the_customer_service__to_retrieve_customers(
    mocker: MockFixture,
):
    expected_customers = mocker.Mock()
    customer_service = mocker.Mock(
        get_all=mocker.Mock(return_value=expected_customers)
    )

    customers_use_case = _use_cases.GetAllCustomerUseCase(customer_service)
    actual_customers = customers_use_case.get_all_customer()

    assert customer_service.get_all.called
    assert expected_customers == actual_customers


def test__get_customer_by_id_function__uses_the_customer_service__to_retrieve_customer(
    mocker: MockFixture,
):
    expected_customer = mocker.Mock()
    customer_service = mocker.Mock(
        get_by_id=mocker.Mock(return_value=expected_customer)
    )

    customer_use_case = _use_cases.GetByIdCustomerUseCase(customer_service)
    actual_customer = customer_use_case.get_customer_by_id(Faker().pyint())

    assert customer_service.get_by_id.called
    assert expected_customer == actual_customer


def test__update_customer_function__uses_the_customer_service__to_update_a_customer(
    mocker: MockFixture, customer_factory
):
    expected_customer = mocker.Mock()
    customer_service = mocker.Mock(
        update=mocker.Mock(return_value=expected_customer)
    )

    customer_use_case = _use_cases.UpdateCustomerUseCase(customer_service)
    updated_customer = customer_use_case.update_customer(Faker().pyint(), customer_factory())

    assert customer_service.update.called
    assert expected_customer == updated_customer
