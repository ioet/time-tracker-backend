import enum

from flask import Flask

from time_tracker_api.database import CRUDDao
from time_tracker_api.sql_repository import SQLCRUDDao, AuditedSQLModel, SQLModel


class PROJECT_TYPE(enum.Enum):
    CUSTOMER = 'CUSTOMER'
    TRAINING = 'TRAINING'

    @classmethod
    def valid_type_values(self):
        return list(map(lambda x: x.value, PROJECT_TYPE._member_map_.values()))


class ProjectDao(CRUDDao):
    pass


def create_dao(app: Flask) -> ProjectDao:
    from time_tracker_api.sql_repository import db

    class ProjectSQLModel(db.Model, SQLModel, AuditedSQLModel):
        __tablename__ = 'projects'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(250), unique=False, nullable=False)
        type = db.Column(db.String(10), nullable=False)
        active = db.Column(db.Boolean, default=True)

        def __repr__(self):
            return '<Project %r>' % self.name

        def __str___(self):
            return "the project \"%s\"" % self.name

    class ProjectSQLDao(SQLCRUDDao):
        def __init__(self):
            SQLCRUDDao.__init__(self, ProjectSQLModel)

    return ProjectSQLDao()
