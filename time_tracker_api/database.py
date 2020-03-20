"""
Agnostic database assets

Put here your utils and class independent of
the database solution.
To know more about protocols and subtyping check out PEP-0544
"""
import abc
import enum
from datetime import datetime

from flask import Flask


class DATABASE_TYPE(enum.Enum):
    IN_MEMORY = 'in-memory'
    SQL = 'sql'


class CRUDDao(abc.ABC):
    @abc.abstractmethod
    def get_all(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, id):
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, project):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, id, data):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id):
        raise NotImplementedError


class Seeder(abc.ABC):
    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

    @abc.abstractmethod
    def fresh(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        self.run()


class DatabaseModel:
    def to_dto(self):
        return self


def convert_result_to_dto(f):
    def convert_if_necessary(result):
        if hasattr(result, 'to_dto'):
            return result.to_dto()
        elif issubclass(type(result), list):
            return list(map(convert_if_necessary, result))
        return result

    def to_dto(*args, **kw):
        result = f(*args, **kw)
        return convert_if_necessary(result)

    return to_dto


seeder: Seeder = None


def init_app(app: Flask) -> None:
    database_strategy = app.config['DATABASE']
    with app.app_context():
        globals()["use_%s" % database_strategy.name.lower()](app)


def use_sql(app: Flask) -> None:
    from time_tracker_api.sql_repository import init_app, SQLSeeder
    init_app(app)
    global seeder
    seeder = SQLSeeder()
