from .. import Project, ProjectService


class CreateProjectUseCase:

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def create_project(self, project_data: Project) -> Project:
        return self.project_service.create(project_data)
