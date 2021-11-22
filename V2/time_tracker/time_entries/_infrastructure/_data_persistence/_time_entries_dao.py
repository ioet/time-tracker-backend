import dataclasses

import sqlalchemy

import time_tracker.time_entries._domain as domain
from time_tracker._infrastructure import _db


class TimeEntriesSQLDao(domain.TimeEntriesDao):

    def __init__(self, database: _db.DB):
        self.time_entry_key = [field.name for field in dataclasses.fields(domain.TimeEntry)]
        self.db = database
        self.time_entry = sqlalchemy.Table(
            'time_entry',
            self.db.metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
            sqlalchemy.Column('start_date', sqlalchemy.DateTime().with_variant(sqlalchemy.String, "sqlite")),
            sqlalchemy.Column('owner_id', sqlalchemy.Integer),
            sqlalchemy.Column('description', sqlalchemy.String),
            sqlalchemy.Column('activity_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('activity.id')),
            sqlalchemy.Column('uri', sqlalchemy.String),
            sqlalchemy.Column(
                'technologies',
                sqlalchemy.ARRAY(sqlalchemy.String).with_variant(sqlalchemy.String, "sqlite")
            ),
            sqlalchemy.Column('end_date', sqlalchemy.DateTime().with_variant(sqlalchemy.String, "sqlite")),
            sqlalchemy.Column('deleted', sqlalchemy.Boolean),
            sqlalchemy.Column('timezone_offset', sqlalchemy.String),
            sqlalchemy.Column('project_id', sqlalchemy.Integer),
            extend_existing=True,
        )

    def create(self, time_entry_data: domain.TimeEntry) -> domain.TimeEntry:
        try:
            new_time_entry = time_entry_data.__dict__
            new_time_entry.pop('id', None)

            query = self.time_entry.insert().values(new_time_entry).return_defaults()
            time_entry = self.db.get_session().execute(query)
            new_time_entry.update({"id": time_entry.inserted_primary_key[0]})
            return self.__create_time_entry_dto(new_time_entry)

        except sqlalchemy.exc.SQLAlchemyError:
            return None

    def update(self, time_entry_id: int, time_entry_data: dict) -> domain.TimeEntry:

        query = self.time_entry.update().where(self.time_entry.c.id == time_entry_id).values(time_entry_data)
        self.db.get_session().execute(query)
        query_deleted_time_entry = sqlalchemy.sql.select(self.time_entry).where(self.time_entry.c.id == time_entry_id)
        time_entry = self.db.get_session().execute(query_deleted_time_entry).one_or_none()

        return self.__create_time_entry_dto(dict(time_entry)) if time_entry else None

    def delete(self, time_entry_id: int) -> domain.TimeEntry:
        query = (
            self.time_entry.update()
            .where(self.time_entry.c.id == time_entry_id)
            .values({"deleted": True})
        )
        self.db.get_session().execute(query)
        query_deleted_time_entry = sqlalchemy.sql.select(self.time_entry).where(self.time_entry.c.id == time_entry_id)
        time_entry = self.db.get_session().execute(query_deleted_time_entry).one_or_none()
        return self.__create_time_entry_dto(dict(time_entry)) if time_entry else None

    def __create_time_entry_dto(self, time_entry: dict) -> domain.TimeEntry:
        time_entry.update({
            "start_date": str(time_entry.get("start_date")),
            "end_date": str(time_entry.get("end_date"))})
        time_entry = {key: time_entry.get(key) for key in self.time_entry_key}
        return domain.TimeEntry(**time_entry)
