import pytest

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


def test__customer_dao__returns_a_customer_dto__when_saves_correctly_with_sql_database(
    test_db, customer_factory, create_fake_dao
):
    dao = create_fake_dao(test_db)

    customer_to_insert = customer_factory()

    inserted_customer = dao.create(customer_to_insert)

    assert isinstance(inserted_customer, domain.Customer)
    assert inserted_customer == customer_to_insert
