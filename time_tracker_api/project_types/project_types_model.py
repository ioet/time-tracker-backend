from time_tracker_api.database import CRUDDao


class ProjectTypeDao(CRUDDao):
    pass


def create_dao() -> ProjectTypeDao:
    from commons.data_access_layer.sql import db
    from time_tracker_api.database import COMMENTS_MAX_LENGTH
    from commons.data_access_layer.sql import SQLCRUDDao
    from sqlalchemy_utils import UUIDType
    import uuid

    class ProjectTypeSQLModel(db.Model):
        __tablename__ = 'project_type'
        id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(COMMENTS_MAX_LENGTH), unique=False, nullable=False)
        parent_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        customer_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        deleted = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        tenant_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)

        def __repr__(self):
            return '<ProjectType %r>' % self.name

        def __str___(self):
            return "the project type \"%s\"" % self.name

    class ProjectTypeSQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, ProjectTypeSQLModel)

    return ProjectTypeSQLDao()
