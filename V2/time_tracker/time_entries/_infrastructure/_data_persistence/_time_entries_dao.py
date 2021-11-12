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

    def __create_time_entry_dto(self, time_entry: dict) -> domain.TimeEntry:
        time_entry = {key: time_entry.get(key) for key in self.time_entry_key}
        return domain.TimeEntry(**time_entry)

    def delete(self, time_entry_id: int) -> TimeEntry:
        time_entry = {
            time_entry.get('id'): time_entry
            for time_entry in self.__get_time_entries_from_file()
        }.get(int(time_entry_id))

        if time_entry:
            time_entry_deleted = {**time_entry, 'deleted': True}

            time_entries_updated = list(
                map(
                    lambda time_entry: time_entry
                    if time_entry.get('id') != time_entry_id
                    else time_entry_deleted,
                    self.__get_time_entries_from_file(),
                )
            )

            try:
                file = open(self.json_data_file_path, 'w')
                json.dump(time_entries_updated, file)
                file.close()

                return self.__create_time_entry_dto(time_entry_deleted)

            except FileNotFoundError:
                return None

        else:
            return None
