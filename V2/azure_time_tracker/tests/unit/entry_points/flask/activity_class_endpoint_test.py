from time_tracker.source.entry_points.flask_api.activities_endpoints import (
    Activities,
    Activity,
)
from time_tracker.source import use_cases
from time_tracker.source.dtos.activity import Activity as ActivityDTO
from pytest_mock import MockFixture
from faker import Faker
from werkzeug.exceptions import NotFound

fake = Faker()

valid_id = fake.uuid4()

fake_activity = {
    "name": fake.company(),
    "description": fake.paragraph(),
    "tenant_id": fake.uuid4(),
    "id": valid_id,
    "deleted": fake.date(),
    "status": fake.boolean(),
}
fake_activity_dto = ActivityDTO(**fake_activity)


def test__activities_class__uses_the_get_activities_use_case__to_retrieve_activities(
    mocker: MockFixture,
):
    mocker.patch.object(
        use_cases.GetActivitiesUseCase,
        'get_activities',
        return_value=[],
    )

    activities_class_endpoint = Activities()
    activities = activities_class_endpoint.get()

    assert use_cases.GetActivitiesUseCase.get_activities.called
    assert [] == activities


def test__activity_class__uses_the_get_activity_by_id_use_case__to_retrieve__an_activity(
    mocker: MockFixture,
):
    mocker.patch.object(
        use_cases.GetActivityUseCase,
        'get_activity_by_id',
        return_value=fake_activity_dto,
    )

    activity_class_endpoint = Activity()
    activity = activity_class_endpoint.get(valid_id)

    assert use_cases.GetActivityUseCase.get_activity_by_id.called
    assert fake_activity == activity
