import typing

from .. import Project, ProjectsDao


class ProjectService:

    def __init__(self, project_dao: ProjectsDao):
        self.project_dao = project_dao

    def create(self, project_data: Project) -> Project:
        return self.project_dao.create(project_data)

    def get_all(self) -> typing.List[Project]:
        return self.project_dao.get_all()

    def get_by_id(self, id: int) -> Project:
        return self.project_dao.get_by_id(id)

    def update(self, id: int, project_data: dict) -> Project:
        return self.project_dao.update(id, project_data)

    def delete(self, id: int) -> Project:
        return self.project_dao.delete(id)
