import typing

from .. import Project, ProjectService


class GetLatestProjectsUseCase:
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def get_latest(self, owner_id: int) -> typing.List[Project]:
        return self.project_service.get_latest(owner_id)
