import enum

from time_tracker_api.database import CRUDDao


class PROJECT_TYPE(enum.Enum):
    CUSTOMER = 'CUSTOMER'
    TRAINING = 'TRAINING'

    @classmethod
    def valid_type_values(self):
        return list(map(lambda x: x.value, PROJECT_TYPE._member_map_.values()))


class ProjectDao(CRUDDao):
    pass


def create_dao() -> ProjectDao:
    from commons.data_access_layer.sql import db
    from time_tracker_api.database import COMMENTS_MAX_LENGTH
    from sqlalchemy_utils import UUIDType
    import uuid
    from commons.data_access_layer.sql import SQLCRUDDao

    class ProjectSQLModel(db.Model):
        __tablename__ = 'project'
        id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(COMMENTS_MAX_LENGTH), unique=False, nullable=False)
        project_type_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        customer_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        deleted = db.Column(UUIDType(binary=False), default=uuid.uuid4)
        tenant_id = db.Column(UUIDType(binary=False), default=uuid.uuid4)

        def __repr__(self):
            return '<Project %r>' % self.name

        def __str___(self):
            return "the project \"%s\"" % self.name

    class ProjectSQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, ProjectSQLModel)

    return ProjectSQLDao()
