from time_tracker_api.database import CRUDDao


class ActivityDao(CRUDDao):
    pass


def create_dao() -> ActivityDao:
    from time_tracker_api.sql_repository import db
    from time_tracker_api.sql_repository import SQLCRUDDao, AuditedSQLModel

    class ActivitySQLModel(db.Model, AuditedSQLModel):
        __tablename__ = 'activity'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(250), unique=False, nullable=False)

        def __repr__(self):
            return '<Activity %r>' % self.name

        def __str___(self):
            return "the activity \"%s\"" % self.name

    class ActivitySQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, ActivitySQLModel)

    return ActivitySQLDao()
