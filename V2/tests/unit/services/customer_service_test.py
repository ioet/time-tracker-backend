from faker import Faker

from time_tracker.customers._domain import CustomerService


def test__create_customer__uses_the_customer_dao__to_create_a_customer(mocker, customer_factory):
    expected_customer = mocker.Mock()
    customer_dao = mocker.Mock(
        create=mocker.Mock(return_value=expected_customer)
    )
    customer_service = CustomerService(customer_dao)

    new_customer = customer_service.create(customer_factory())

    assert customer_dao.create.called
    assert expected_customer == new_customer


def test__delete_customer__uses_the_customer_dao__to_delete_customer_selected(
    mocker,
):
    expected_customer = mocker.Mock()
    customer_dao = mocker.Mock(
        delete=mocker.Mock(return_value=expected_customer)
    )

    customer_service = CustomerService(customer_dao)
    deleted_customer = customer_service.delete(Faker().pyint())

    assert customer_dao.delete.called
    assert expected_customer == deleted_customer


def test__get_all__uses_the_customer_dao__to_retrieve_customers(mocker):
    expected_customers = mocker.Mock()
    customer_dao = mocker.Mock(
        get_all=mocker.Mock(return_value=expected_customers)
    )
    customer_service = CustomerService(customer_dao)

    actual_customers = customer_service.get_all()

    assert customer_dao.get_all.called
    assert expected_customers == actual_customers


def test__get_by_id__uses_the_customer_dao__to_retrieve_one_customer(mocker):
    expected_customer = mocker.Mock()
    customer_dao = mocker.Mock(
        get_by_id=mocker.Mock(return_value=expected_customer)
    )
    customer_service = CustomerService(customer_dao)

    actual_customer = customer_service.get_by_id(Faker().pyint())

    assert customer_dao.get_by_id.called
    assert expected_customer == actual_customer


def test__update_customer__uses_the_customer_dao__to_update_a_customer(mocker, customer_factory):
    expected_customer = mocker.Mock()
    customer_dao = mocker.Mock(
        update=mocker.Mock(return_value=expected_customer)
    )
    customer_service = CustomerService(customer_dao)

    updated_customer = customer_service.update(Faker().pyint(), customer_factory())

    assert customer_dao.update.called
    assert expected_customer == updated_customer
