import dataclasses
import typing

import sqlalchemy
import sqlalchemy.sql as sql

import time_tracker.activities._domain as domain
from time_tracker._infrastructure import _db


class ActivitiesSQLDao(domain.ActivitiesDao):

    def __init__(self, database: _db.DB):
        self.activity_keys = [
            field.name for field in dataclasses.fields(domain.Activity)
        ]
        self.db = database
        self.activity = sqlalchemy.Table(
            'activity',
            self.db.metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
            sqlalchemy.Column('name', sqlalchemy.String),
            sqlalchemy.Column('description', sqlalchemy.String),
            sqlalchemy.Column('deleted', sqlalchemy.Boolean),
            sqlalchemy.Column('status', sqlalchemy.SmallInteger),
            extend_existing=True,
        )

    def get_by_id(self, activity_id: str) -> domain.Activity:
        query = sql.select(self.activity).where(self.activity.c.id == activity_id)
        activity = self.db.get_session().execute(query).one_or_none()
        return self.__create_activity_dto(dict(activity)) if activity else None

    def get_all(self) -> typing.List[domain.Activity]:
        query = sql.select(self.activity)
        result = self.db.get_session().execute(query)
        return [
            self.__create_activity_dto(dict(activity))
            for activity in result
        ]

    def create(self, activity_data: dict) -> domain.Activity:
        activity_data.pop('id', None)
        activity_data.update({"status": 1, "deleted": False})
        query = self.activity.insert().values(activity_data).return_defaults()
        activity = self.db.get_session().execute(query)
        activity_data.update({"id": activity.inserted_primary_key[0]})
        return self.__create_activity_dto(activity_data)

    def delete(self, activity_id: str) -> domain.Activity:
        query = self.activity.update().where(self.activity.c.id == activity_id).values({"status": 0, "deleted": True})
        self.db.get_session().execute(query)
        return self.get_by_id(activity_id)

    def update(self, activity_id: str, new_activity: dict) -> domain.Activity:
        new_activity.pop('id', None)
        query = self.activity.update().where(self.activity.c.id == activity_id).values(new_activity)
        self.db.get_session().execute(query)
        return self.get_by_id(activity_id)

    def __create_activity_dto(self, activity: dict) -> domain.Activity:
        activity = {key: activity.get(key)for key in self.activity_keys}
        return domain.Activity(**activity)
