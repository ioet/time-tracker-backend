from http import HTTPStatus

from azure.cosmos.exceptions import CosmosResourceNotFoundError

from time_tracker_api.projects import projects_model
from time_tracker_api.activities import activities_model


def are_related_entry_entities_valid(project_id: str, activity_id: str):
    if not project_id:
        return {
            "is_valid": False,
            "status_code": HTTPStatus.BAD_REQUEST,
            "message": "Project id can not be empty",
        }

    if not activity_id:
        return {
            "is_valid": False,
            "status_code": HTTPStatus.BAD_REQUEST,
            "message": "Activity id can not be empty",
        }

    exists_project = exists_related_entity(
        project_id, projects_model.create_dao()
    )

    if not exists_project:
        return {
            "is_valid": False,
            "status_code": HTTPStatus.BAD_REQUEST,
            "message": "Related Project does not exists",
        }

    exists_activity = exists_related_entity(
        activity_id, activities_model.create_dao()
    )

    if not exists_activity:
        return {
            "is_valid": False,
            "status_code": HTTPStatus.BAD_REQUEST,
            "message": "Related Activity does not exists",
        }

    return {
        "is_valid": True,
        "status_code": HTTPStatus.OK,
        "message": "Related entry entities valid",
    }


def exists_related_entity(related_id: str, dao):
    try:
        dao.get(related_id)
        return True
    except CosmosResourceNotFoundError:
        return False
