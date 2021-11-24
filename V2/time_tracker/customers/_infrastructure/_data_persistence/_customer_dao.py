import dataclasses
import typing

import sqlalchemy as sq
import sqlalchemy.sql as sql

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

    def get_by_id(self, id: int) -> domain.Customer:
        query = sql.select(self.customer).where(
            sql.and_(self.customer.c.id == id, self.customer.c.deleted.is_(False))
            )
        customer = self.db.get_session().execute(query).one_or_none()
        return self.__create_customer_dto(dict(customer)) if customer else None

    def get_all(self) -> typing.List[domain.Customer]:
        query = sq.sql.select(self.customer).where(self.customer.c.deleted.is_(False))
        result = self.db.get_session().execute(query)
        return [
            self.__create_customer_dto(dict(customer))
            for customer in result
        ]

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

    def delete(self, customer_id: int) -> domain.Customer:
        query = (
            self.customer.update()
            .where(self.customer.c.id == customer_id)
            .values({"deleted": True})
        )
        self.db.get_session().execute(query)
        query_deleted_customer = sq.sql.select(self.customer).where(self.customer.c.id == customer_id)
        customer = self.db.get_session().execute(query_deleted_customer).one_or_none()
        return self.__create_customer_dto(dict(customer)) if customer else None

    def update(self, id: int, data: domain.Customer) -> domain.Customer:
        try:
            new_customer = {
                "name": data.name,
                "description": data.description,
                "status": data.status,
                "deleted": data.deleted
            }
            customer_validated = {key: value for (key, value) in new_customer.items() if value is not None}
            query = self.customer.update().where(self.customer.c.id == id).values(customer_validated)
            self.db.get_session().execute(query)
            return self.get_by_id(id)
        except sq.exc.SQLAlchemyError:
            return None
