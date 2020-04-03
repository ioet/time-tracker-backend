from time_tracker_api.database import CRUDDao


class ActivityDao(CRUDDao):
    pass


def create_dao() -> ActivityDao:
    from time_tracker_api.sql_repository import db
    from time_tracker_api.sql_repository import SQLCRUDDao
    from sqlalchemy_utils import UUIDType
    import uuid

    class ActivitySQLModel(db.Model):
        __tablename__ = 'activity'
        id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(250), unique=False, nullable=False)
        deleted = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        tenant_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)

        def __repr__(self):
            return '<Activity %r>' % self.name

        def __str___(self):
            return "the activity \"%s\"" % self.name

    class ActivitySQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, ActivitySQLModel)

    return ActivitySQLDao()
