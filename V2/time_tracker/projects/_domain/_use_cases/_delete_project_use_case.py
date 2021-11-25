from .. import Project, ProjectService


class DeleteProjectUseCase:

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def delete_project(self, id: int) -> Project:
        return self.project_service.delete(id)
