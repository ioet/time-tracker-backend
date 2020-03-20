import enum

from flask import Flask

from time_tracker_api.database import DATABASE_TYPE, CRUDDao
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
    if app.config['DATABASE'] == DATABASE_TYPE.SQL:
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
    else:
        """
        This is legacy, just to make clear how multiple database strategies can be supported
        with the current design/architecture.
        """
        from time_tracker_api.errors import MissingResource

        class ProjectInMemoryDAO(object):
            def __init__(self):
                self.counter = 0
                self.projects = []

            def get_all(self):
                return self.projects

            def get(self, id):
                for project in self.projects:
                    if project.get('id') == id:
                        return project
                raise MissingResource("Project '%s' not found" % id)

            def create(self, project):
                self.counter += 1
                project['id'] = str(self.counter)
                self.projects.append(project)
                return project

            def update(self, id, data):
                project = self.get(id)
                if project:
                    project.update(data)
                    return project
                else:
                    raise MissingResource("Project '%s' not found" % id)

            def delete(self, id):
                if id:
                    project = self.get(id)
                    self.projects.remove(project)

        return ProjectInMemoryDAO()
