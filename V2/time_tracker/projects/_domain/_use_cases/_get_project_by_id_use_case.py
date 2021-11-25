from .. import ProjectService, Project


class GetProjectUseCase:
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def get_project_by_id(self, id: int) -> Project:
        return self.project_service.get_by_id(id)
