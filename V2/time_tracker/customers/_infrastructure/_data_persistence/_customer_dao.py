import dataclasses
import sqlalchemy as sq

import time_tracker.customers._domain as domain
from time_tracker._infrastructure import _db


class CustomersSQLDao(domain.CustomersDao):

    def __init__(self, database: _db.DB):
        self.customer_key = [field.name for field in dataclasses.fields(domain.Customer)]
        self.db = database
        self.customer = sq.Table(
            'customer',
            self.db.metadata,
            sq.Column('id', sq.Integer, primary_key=True, autoincrement=True),
            sq.Column('name', sq.String, unique=True, nullable=False),
            sq.Column('description', sq.String),
            sq.Column('deleted', sq.Boolean),
            sq.Column('status', sq.Integer),
            extend_existing=True,
        )

    def create(self, data: domain.Customer) -> domain.Customer:
        try:
            new_customer = data.__dict__
            new_customer.pop('id', None)
            new_customer['deleted'] = False
            new_customer['status'] = 1

            query = self.customer.insert().values(new_customer).return_defaults()
            customer = self.db.get_session().execute(query)
            new_customer.update({"id": customer.inserted_primary_key[0]})
            return self.__create_customer_dto(new_customer)
        except sq.exc.IntegrityError:
            return None

    def __create_customer_dto(self, customer: dict) -> domain.Customer:
        customer = {key: customer.get(key) for key in self.customer_key}
        return domain.Customer(**customer)
