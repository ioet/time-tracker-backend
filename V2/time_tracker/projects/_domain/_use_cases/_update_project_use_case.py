from .. import ProjectService, Project


class UpdateProjectUseCase:
    def __init__(self, projects_service: ProjectService):
        self.projects_service = projects_service

    def update_project(
        self, id: int, name: str, description: str, customer_id: int, status: int
    ) -> Project:
        return self.projects_service.update(id, name, description, customer_id, status)
