import copy
from unittest.mock import Mock, patch, ANY
from faker import Faker
from commons.data_access_layer.database import EventContext
from time_tracker_api.activities.activities_model import (
    ActivityCosmosDBRepository,
    ActivityCosmosDBModel,
    create_dao,
)

faker = Faker()


@patch(
    'time_tracker_api.activities.activities_model.ActivityCosmosDBRepository.find_partition_key_value'
)
def test_find_all_with_id_in_list(
    find_partition_key_value_mock,
    event_context: EventContext,
    activity_repository: ActivityCosmosDBRepository,
):
    expected_item = {
        'id': faker.uuid4(),
        'name': faker.name(),
        'description': faker.sentence(nb_words=4),
        'tenant_id': faker.uuid4(),
    }

    query_items_mock = Mock(return_value=[expected_item])
    activity_repository.container = Mock()
    activity_repository.container.query_items = query_items_mock

    result = activity_repository.find_all_with_id_in_list(
        event_context, [expected_item]
    )

    find_partition_key_value_mock.assert_called_once()
    query_items_mock.assert_called_once()

    assert len(result) == 1
    activity = result[0]
    assert isinstance(activity, ActivityCosmosDBModel)
    assert activity.__dict__ == expected_item


def test_create_activity_should_add_active_status(
    mocker,
):
    activity_payload = {
        'name': faker.name(),
        'description': faker.sentence(nb_words=5),
        'tenant_id': faker.uuid4(),
    }
    activity_repository_create_mock = mocker.patch.object(
        ActivityCosmosDBRepository, 'create'
    )

    activity_dao = create_dao()
    activity_dao.create(activity_payload)

    expect_argument = copy.copy(activity_payload)
    expect_argument['status'] = 'active'
    activity_repository_create_mock.assert_called_with(
        data=expect_argument, event_context=ANY
    )
