import typing
import dataclasses

import sqlalchemy as sq

from ... import _domain as domain
from time_tracker._infrastructure import _db
from time_tracker.time_entries._infrastructure._data_persistence import TimeEntriesSQLDao
from time_tracker.customers._infrastructure._data_persistence import CustomersSQLDao


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
            validated_project = {key: value for (key, value) in project_data.__dict__.items() if value is not None}

            query = self.project.insert().values(validated_project).return_defaults()

            project = self.db.get_session().execute(query)
            return self.get_by_id(project.inserted_primary_key[0])

        except sq.exc.SQLAlchemyError:
            return None

    def get_by_id(self, id: int) -> domain.Project:
        """
        query = sq.sql.text(
            "SELECT project.*, json_array((customer.*)) AS customer FROM project "
            "JOIN customer ON customer.id=project.customer_id "
            "WHERE project.id=:id GROUP BY project.id "
        )
        """
        query = sq.sql.select(self.project).where(self.project.c.id == id)
        project = self.db.get_session().execute(query).one_or_none()
        if project:
            customer_model = CustomersSQLDao(self.db).customer
            query_customer = sq.sql.select(customer_model).where(customer_model.c.id == project["customer_id"])
            customer = self.db.get_session().execute(query_customer).one_or_none()
            project = dict(project)
            project.update({"customer": dict(customer)if customer else None})

        return self.__create_project_dto(project) if project else None

    def get_all(self) -> typing.List[domain.Project]:
        """
        query = sq.sql.text(
            "SELECT project.*, json_array((customer.*)) AS customer FROM project "
            "JOIN customer ON customer.id=project.customer_id GROUP BY project.id"
        )
        """
        customer_model = CustomersSQLDao(self.db).customer
        query = sq.sql.select(self.project, customer_model).join(customer_model)
        result = self.db.get_session().execute(query).all()
        projects = []

        for project in result:
            query_customer = sq.sql.select(customer_model).where(customer_model.c.id == project["customer_id"])
            customer = self.db.get_session().execute(query_customer).one_or_none()
            project = dict(project)
            project.update({"customer": dict(customer)if customer else None})
            projects.append(project)

        return [
            self.__create_project_dto(project)
            for project in projects
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
        try:
            query = self.project.update().where(self.project.c.id == id).values(project_data)
            self.db.get_session().execute(query)
            return self.get_by_id(id)
        except sq.exc.SQLAlchemyError as error:
            raise Exception(error.orig)

    def get_latest(self, owner_id: int) -> typing.List[domain.Project]:
        time_entries_dao = TimeEntriesSQLDao(self.db)
        latest_time_entries = time_entries_dao.get_latest_entries(owner_id)
        latest_projects = []
        if latest_time_entries:
            filter_project = typing.Counter(time_entry['project_id'] for time_entry in latest_time_entries)
            latest_projects = [self.get_by_id(project_id) for project_id in filter_project]

        return latest_projects

    def __create_project_dto(self, project: dict) -> domain.Project:
        project = {key: project.get(key) for key in self.project_key}
        return domain.Project(**project)
