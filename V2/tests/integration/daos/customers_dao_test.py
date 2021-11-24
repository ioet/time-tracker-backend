import pytest
import typing
from faker import Faker

import time_tracker.customers._domain as domain
import time_tracker.customers._infrastructure as infrastructure
from time_tracker._infrastructure import DB


@pytest.fixture(name='create_fake_dao')
def _fake_dao() -> domain.CustomersDao:
    def _create_fake_dao(db_fake: DB) -> domain.CustomersDao:
        dao = infrastructure.CustomersSQLDao(db_fake)
        return dao
    return _create_fake_dao


@pytest.fixture(name='clean_database', autouse=True)
def _clean_database():
    yield
    db_fake = DB()
    dao = infrastructure.CustomersSQLDao(db_fake)
    query = dao.customer.delete()
    dao.db.get_session().execute(query)


def test__create_customer_dao__returns_a_customer_dto__when_saves_correctly_with_sql_database(
    test_db, customer_factory, create_fake_dao
):
    dao = create_fake_dao(test_db)

    customer_to_insert = customer_factory()

    inserted_customer = dao.create(customer_to_insert)

    assert isinstance(inserted_customer, domain.Customer)
    assert inserted_customer == customer_to_insert


def test__get_all__returns_a_list_of_customer_dto_objects__when_one_or_more_customers_are_found_with_sql_database(
    test_db, create_fake_dao, customer_factory, insert_customer
):
    dao = create_fake_dao(test_db)
    customer_to_insert = customer_factory()
    inserted_customer = [dao.create(customer_to_insert)]

    customers = dao.get_all()

    assert isinstance(customers, typing.List)
    assert customers == inserted_customer


def test_get_by_id__returns_a_customer_dto__when_found_one_customer_that_matches_its_id_with_sql_database(
    test_db, create_fake_dao, customer_factory, insert_customer
):
    dao = create_fake_dao(test_db)
    existent_customer = customer_factory()
    inserted_customer = insert_customer(existent_customer, dao.db)

    customer = dao.get_by_id(inserted_customer.id)

    assert isinstance(customer, domain.Customer)
    assert customer.id == inserted_customer.id
    assert customer == inserted_customer


def test__get_by_id__returns_none__when_no_customer_matches_its_id_with_sql_database(
    test_db, create_fake_dao, customer_factory
):
    dao = create_fake_dao(test_db)
    existent_customer = customer_factory()

    customer = dao.get_by_id(existent_customer.id)

    assert customer is None


def test_get_all__returns_an_empty_list__when_doesnt_found_any_customers_with_sql_database(
    test_db, create_fake_dao
):
    customers = create_fake_dao(test_db).get_all()

    assert isinstance(customers, typing.List)
    assert customers == []


def test_delete__returns_a_customer_with_inactive_status__when_a_customer_matching_its_id_is_found_with_sql_database(
    test_db, create_fake_dao, customer_factory, insert_customer
):
    dao = create_fake_dao(test_db)
    existent_customer = customer_factory()
    inserted_customer = insert_customer(existent_customer, dao.db)

    customer = dao.delete(inserted_customer.id)

    assert isinstance(customer, domain.Customer)
    assert customer.id == inserted_customer.id
    assert customer.status == 1
    assert customer.deleted is True


def test_delete__returns_none__when_no_customer_matching_its_id_is_found_with_sql_database(
    test_db, create_fake_dao, customer_factory
):
    dao = create_fake_dao(test_db)
    existent_customer = customer_factory()

    results = dao.delete(existent_customer.id)

    assert results is None


def test__update_customer_dao__returns_an_updated_customer_dto__when_updates_correctly_with_sql_database(
    test_db, customer_factory, create_fake_dao, insert_customer
):
    dao = create_fake_dao(test_db)

    existent_customer = customer_factory()
    inserted_customer = insert_customer(existent_customer, dao.db).__dict__

    inserted_customer["description"] = Faker().sentence()

    updated_customer = dao.update(inserted_customer["id"], domain.Customer(**inserted_customer))

    assert isinstance(updated_customer, domain.Customer)
    assert updated_customer.description == inserted_customer["description"]
    assert updated_customer.__dict__ == inserted_customer


def test__update_customer_dao__returns_None__when_an_incorrect_id_is_passed(
    test_db, customer_factory, create_fake_dao, insert_customer
):
    dao = create_fake_dao(test_db)
    existent_customer = customer_factory()

    updated_customer = dao.update(Faker().pyint(), existent_customer)

    assert updated_customer is None
