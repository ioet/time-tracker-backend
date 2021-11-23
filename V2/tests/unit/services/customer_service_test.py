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
