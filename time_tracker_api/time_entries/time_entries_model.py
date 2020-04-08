from sqlalchemy_utils import ScalarListType

from time_tracker_api.database import CRUDDao


class TimeEntriesDao(CRUDDao):
    pass


def create_dao() -> TimeEntriesDao:
    from commons.data_access_layer.sql import db
    from time_tracker_api.database import COMMENTS_MAX_LENGTH
    from sqlalchemy_utils import UUIDType
    import uuid
    from commons.data_access_layer.sql import SQLCRUDDao

    class TimeEntrySQLModel(db.Model):
        __tablename__ = 'time_entry'
        id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
        description = db.Column(db.String(COMMENTS_MAX_LENGTH))
        start_date = db.Column(db.DateTime, server_default=db.func.now())
        end_date = db.Column(db.DateTime)
        project_id = db.Column(UUIDType(binary=False),
                               db.ForeignKey('project.id'),
                               nullable=False)
        activity_id = db.Column(UUIDType(binary=False),
                                db.ForeignKey('activity.id'),
                                nullable=False)
        technologies = db.Column(ScalarListType())
        uri = db.Column(db.String(500))
        owner_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        deleted = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        tenant_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)

        @property
        def running(self):
            return self.end_date is None

        def __repr__(self):
            return '<Time Entry %r>' % self.start_date

        def __str___(self):
            return "Time Entry started in \"%s\"" % self.start_date

    class TimeEntriesSQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, TimeEntrySQLModel)

    return TimeEntriesSQLDao()
