"""
Agnostic database assets

Put here your utils and class independent of
the database solution.
To know more about protocols and subtyping check out PEP-0544
"""
import abc

from flask import Flask


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
    pass


seeder: Seeder = None


def init_app(app: Flask) -> None:
    from time_tracker_api.sql_repository import init_app, SQLSeeder
    init_app(app)
    global seeder
    seeder = SQLSeeder()
