import typing
import dataclasses

import sqlalchemy as sq

from ... import _domain as domain
from time_tracker._infrastructure import _db


class ProjectsSQLDao(domain.ProjectsDao):

    def __init__(self, database: _db.DB):
        self.project_key = [field.name for field in dataclasses.fields(domain.Project)]
        self.db = database
        self.project = sq.Table(
            'project',
            self.db.metadata,
            sq.Column('id', sq.Integer, primary_key=True, autoincrement=True),
            sq.Column('name', sq.String),
            sq.Column('description', sq.String),
            sq.Column('project_type_id', sq.Integer),
            sq.Column('customer_id', sq.Integer, sq.ForeignKey('customer.id')),
            sq.Column('status', sq.SmallInteger),
            sq.Column('deleted', sq.BOOLEAN),
            sq.Column(
                'technologies',
                sq.ARRAY(sq.String).with_variant(sq.String, "sqlite")
            ),
            extend_existing=True,
        )

    def create(self, project_data: domain.Project) -> domain.Project:
        try:
            new_project = project_data.__dict__
            new_project.pop('id', None)

            query = self.project.insert().values(new_project).return_defaults()
            project = self.db.get_session().execute(query)
            new_project.update({"id": project.inserted_primary_key[0]})
            return self.__create_project_dto(new_project)

        except sq.exc.SQLAlchemyError:
            return None

    def get_by_id(self, id: int) -> domain.Project:
        query = sq.sql.select(self.project).where(self.project.c.id == id)
        project = self.db.get_session().execute(query).one_or_none()
        return self.__create_project_dto(dict(project)) if project else None

    def get_all(self) -> typing.List[domain.Project]:
        query = sq.sql.select(self.project)
        result = self.db.get_session().execute(query)
        return [
            self.__create_project_dto(dict(project))
            for project in result
        ]

    def delete(self, id: int) -> domain.Project:
        query = (
            self.project.update()
            .where(self.project.c.id == id)
            .values({"deleted": True, "status": 0})
        )
        self.db.get_session().execute(query)
        return self.get_by_id(id)

    def update(self, id: int, project_data: dict) -> domain.Project:
        query = self.project.update().where(self.project.c.id == id).values(project_data)
        self.db.get_session().execute(query)
        return self.get_by_id(id)

    def __create_project_dto(self, project: dict) -> domain.Project:
        project = {key: project.get(key) for key in self.project_key}
        return domain.Project(**project)
