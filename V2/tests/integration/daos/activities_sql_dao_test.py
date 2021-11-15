import pytest
import typing
from faker import Faker

import time_tracker.activities._domain as domain
import time_tracker.activities._infrastructure as infrastructure
from time_tracker._infrastructure import DB


@pytest.fixture(name='insert_activity')
def _insert_activity() -> domain.Activity:
    def _new_activity(activity: domain.Activity, dao: domain.ActivitiesDao):
        new_activity = dao.create(activity)
        return new_activity
    return _new_activity


@pytest.fixture(name='clean_database', autouse=True)
def _clean_database():
    yield
    db_fake = DB('sqlite:///:memory:')
    dao = infrastructure.ActivitiesSQLDao(db_fake)
    query = dao.activity.delete()
    dao.db.get_session().execute(query)


def test__create_activity__returns_a_activity_dto__when_saves_correctly_with_sql_database(
    create_fake_dao, activity_factory
):
    dao = create_fake_dao
    existent_activity = activity_factory()

    inserted_activity = dao.create(existent_activity)

    assert isinstance(inserted_activity, domain.Activity)
    assert inserted_activity == existent_activity


def test_update__returns_an_update_activity__when_an_activity_matching_its_id_is_found_with_sql_database(
    create_fake_dao, activity_factory, insert_activity
):
    dao = create_fake_dao
    existent_activity = activity_factory()
    inserted_activity = insert_activity(existent_activity, dao)

    expected_description = Faker().sentence()
    updated_activity = dao.update(inserted_activity.id, None, expected_description, None, None)

    assert isinstance(updated_activity, domain.Activity)
    assert updated_activity.id == inserted_activity.id
    assert updated_activity.description == expected_description


def test_update__returns_none__when_no_activity_matching_its_id_is_found_with_sql_database(
    create_fake_dao, activity_factory
):
    dao = create_fake_dao
    existent_activity = activity_factory()

    results = dao.update(existent_activity.id, Faker().name(), None, None, None)

    assert results is None


def test__get_all__returns_a_list_of_activity_dto_objects__when_one_or_more_activities_are_found_with_sql_database(
    create_fake_dao, activity_factory, insert_activity
):
    dao = create_fake_dao
    existent_activities = [activity_factory(), activity_factory()]
    inserted_activities = [
        insert_activity(existent_activities[0], dao),
        insert_activity(existent_activities[1], dao)
    ]

    activities = dao.get_all()

    assert isinstance(activities, typing.List)
    assert activities == inserted_activities


def test_get_by_id__returns_an_activity_dto__when_found_one_activity_that_matches_its_id_with_sql_database(
    create_fake_dao, activity_factory, insert_activity
):
    dao = create_fake_dao
    existent_activity = activity_factory()
    inserted_activity = insert_activity(existent_activity, dao)

    activity = dao.get_by_id(inserted_activity.id)

    assert isinstance(activity, domain.Activity)
    assert activity.id == inserted_activity.id
    assert activity == inserted_activity


def test__get_by_id__returns_none__when_no_activity_matches_its_id_with_sql_database(
    create_fake_dao, activity_factory
):
    dao = create_fake_dao
    existent_activity = activity_factory()

    activity = dao.get_by_id(existent_activity.id)

    assert activity is None


def test_get_all__returns_an_empty_list__when_doesnt_found_any_activities_with_sql_database(
    create_fake_dao
):
    activities = create_fake_dao.get_all()

    assert isinstance(activities, typing.List)
    assert activities == []


def test_delete__returns_an_activity_with_inactive_status__when_an_activity_matching_its_id_is_found_with_sql_database(
    create_fake_dao, activity_factory, insert_activity
):
    dao = create_fake_dao
    existent_activity = activity_factory()
    inserted_activity = insert_activity(existent_activity, dao)

    activity = dao.delete(inserted_activity.id)

    assert isinstance(activity, domain.Activity)
    assert activity.id == inserted_activity.id
    assert activity.status == 0
    assert activity.deleted is True


def test_delete__returns_none__when_no_activity_matching_its_id_is_found_with_sql_database(
    create_fake_dao, activity_factory
):
    dao = create_fake_dao
    existent_activity = activity_factory()

    results = dao.delete(existent_activity.id)

    assert results is None
