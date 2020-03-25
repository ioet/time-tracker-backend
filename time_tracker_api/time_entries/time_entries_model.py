from sqlalchemy_utils import ScalarListType

from time_tracker_api.database import CRUDDao

COMMENTS_MAX_NUMBER_CHARS = 500


class TimeEntriesDao(CRUDDao):
    pass


def create_dao() -> TimeEntriesDao:
    from time_tracker_api.sql_repository import db
    from time_tracker_api.sql_repository import SQLCRUDDao, AuditedSQLModel, SQLModel

    class TimeEntrySQLModel(db.Model, SQLModel, AuditedSQLModel):
        __tablename__ = 'time_entry'
        id = db.Column(db.Integer, primary_key=True)
        description = db.Column(db.String(COMMENTS_MAX_NUMBER_CHARS))
        start_date = db.Column(db.DateTime, server_default=db.func.now())
        end_date = db.Column(db.DateTime)
        project_id = db.Column(db.Integer,
                               db.ForeignKey('project.id'),
                               nullable=False)
        activity_id = db.Column(db.Integer,
                                db.ForeignKey('activity.id'),
                                nullable=False)

        technologies = db.Column(ScalarListType())

        @property
        def running(self):
            return self.end_date == None

        # @property
        # def technologies(self):
        #     return [str(x) for x in self._technologies.split(';')]
        #
        # @technologies.setter
        # def technologies(self, value):
        #     if value is Iterable:
        #         self._technologies = LIST_SEPARATOR_CHAR.join(value)
        #     elif type(value) == str:
        #         self._technologies = value
        #     else:
        #         raise UnprocessableEntity

        def __repr__(self):
            return '<Time Entry %r>' % self.start_date

        def __str___(self):
            return "Time Entry started in \"%s\"" % self.start_date

    class TimeEntriesSQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, TimeEntrySQLModel)

    return TimeEntriesSQLDao()
