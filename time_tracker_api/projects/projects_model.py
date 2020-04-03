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
    from time_tracker_api.sql_repository import db
    from time_tracker_api.database import COMMENTS_MAX_LENGTH
    from time_tracker_api.sql_repository import SQLCRUDDao, AuditedSQLModel

    class ProjectSQLModel(db.Model):
        __tablename__ = 'project'
        id = db.Column(db.String, primary_key=True)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(COMMENTS_MAX_LENGTH), unique=False, nullable=False)
        project_type_id = db.Column(db.String, default=None)
        customer_id = db.Column(db.String, nullable=False)
        deleted = db.Column(db.String, default=None)
        tenant_id = db.Column(db.String, nullable=False)

        def __repr__(self):
            return '<Project %r>' % self.name

        def __str___(self):
            return "the project \"%s\"" % self.name

    class ProjectSQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, ProjectSQLModel)

    return ProjectSQLDao()
