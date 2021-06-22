from http import HTTPStatus

from azure.cosmos.exceptions import CosmosResourceNotFoundError
from faker import Faker

from time_tracker_api.activities import activities_model
from time_tracker_api.activities.activities_model import ActivityCosmosDBDao
from time_tracker_api.projects.projects_model import ProjectCosmosDBDao
from utils.validate_entries import (
    are_related_entry_entities_valid,
    exists_related_entity,
)

fake = Faker()


def test_validate_related_entry_entities_must_failed_if_project_id_is_empty():
    are_entities_valid = are_related_entry_entities_valid(
        project_id=None, activity_id=fake.uuid4()
    )

    assert are_entities_valid.get('is_valid') is False
    assert are_entities_valid.get('status_code') == HTTPStatus.BAD_REQUEST
    assert are_entities_valid.get('message') == "Project id can not be empty"


def test_validate_related_entry_entities_must_failed_if_activity_id_is_empty():
    are_entities_valid = are_related_entry_entities_valid(
        project_id=fake.uuid4(), activity_id=None
    )

    assert are_entities_valid.get('is_valid') is False
    assert are_entities_valid.get('status_code') == HTTPStatus.BAD_REQUEST
    assert are_entities_valid.get('message') == "Activity id can not be empty"


def test_validate_related_entry_entities_must_pass_if_the_data_is_valid(
    mocker,
):
    mocker.patch.object(ProjectCosmosDBDao, 'get')
    mocker.patch.object(ActivityCosmosDBDao, 'get')

    are_entities_valid = are_related_entry_entities_valid(
        project_id=fake.uuid4(), activity_id=fake.uuid4()
    )

    assert are_entities_valid.get('is_valid') is True
    assert are_entities_valid.get('status_code') == HTTPStatus.OK
    assert are_entities_valid.get('message') == 'Related entry entities valid'


def test_validate_related_entry_entities_must_fail_if_the_project_id_does_not_exists(
    mocker,
):
    mocker.patch(
        'utils.validate_entries.exists_related_entity', return_value=False
    )

    are_entities_valid = are_related_entry_entities_valid(
        project_id=fake.uuid4(), activity_id=fake.uuid4()
    )

    assert are_entities_valid.get('is_valid') is False
    assert are_entities_valid.get('status_code') == HTTPStatus.BAD_REQUEST
    assert (
        are_entities_valid.get('message') == 'Related Project does not exists'
    )


def test_validate_related_entry_entities_must_fail_if_the_activity_id_does_not_exists(
    mocker,
):
    mocker.patch.object(ProjectCosmosDBDao, 'get')

    mocker.patch.object(
        ActivityCosmosDBDao, 'get', side_effect=CosmosResourceNotFoundError
    )

    are_entities_valid = are_related_entry_entities_valid(
        project_id=fake.uuid4(), activity_id=fake.uuid4()
    )

    assert are_entities_valid.get('is_valid') is False
    assert are_entities_valid.get('status_code') == HTTPStatus.BAD_REQUEST
    assert (
        are_entities_valid.get('message') == 'Related Activity does not exists'
    )


def test_exists_related_entity_should_return_true_if_entity_exists(mocker):
    mocker.patch.object(ActivityCosmosDBDao, 'get')
    activity_dao = activities_model.create_dao()

    exists_entity = exists_related_entity(
        related_id=fake.uuid4(), dao=activity_dao
    )

    assert exists_entity is True


def test_exists_related_entity_should_return_false_if_entity_does_not_exists(
    mocker,
):
    mocker.patch.object(
        ActivityCosmosDBDao, 'get', side_effect=CosmosResourceNotFoundError
    )
    activity_dao = activities_model.create_dao()

    exists_entity = exists_related_entity(
        related_id=fake.uuid4(), dao=activity_dao
    )

    assert exists_entity is False
