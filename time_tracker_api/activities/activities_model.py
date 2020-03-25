from time_tracker_api.database import CRUDDao


class ActivitiesDao(CRUDDao):
    pass


def create_dao() -> ActivitiesDao:
    from time_tracker_api.sql_repository import db
    from time_tracker_api.sql_repository import SQLCRUDDao, AuditedSQLModel, SQLModel

    class ActivitySQLModel(db.Model, SQLModel, AuditedSQLModel):
        __tablename__ = 'activity'
        id = db.Column(db.Integer, primary_key=True)

    class ActivitiesSQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, ActivitySQLModel)

    return ActivitiesSQLDao()
