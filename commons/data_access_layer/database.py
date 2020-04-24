"""
Agnostic database assets

Put here your utils and class independent of
the database solution.
To know more about protocols and subtyping check out PEP-0544
"""
import abc

from flask import Flask

COMMENTS_MAX_LENGTH = 500
ID_MAX_LENGTH = 64


class CRUDDao(abc.ABC):
    @abc.abstractmethod
    def get_all(self, conditions: dict):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def get(self, id):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def create(self, project):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def update(self, id, data):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def delete(self, id):
        raise NotImplementedError  # pragma: no cover


def init_app(app: Flask) -> None:
    init_cosmos_db(app)


def init_sql(app: Flask) -> None:
    from commons.data_access_layer.sql import init_app
    init_app(app)


def init_cosmos_db(app: Flask) -> None:
    from commons.data_access_layer.cosmos_db import init_app
    init_app(app)
