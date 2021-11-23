import typing

from .. import Project, ProjectService


class GetProjectsUseCase:
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def get_projects(self) -> typing.List[Project]:
        return self.project_service.get_all()
