from .. import ProjectService, Project


class UpdateProjectUseCase:
    def __init__(self, projects_service: ProjectService):
        self.projects_service = projects_service

    def update_project(self, id: int, project_data: dict) -> Project:
        return self.projects_service.update(id, project_data)
