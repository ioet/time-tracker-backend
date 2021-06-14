from utils.azure_users import AzureConnection, AzureUser
from time_tracker_api.time_entries.time_entries_repository import (
    TimeEntryCosmosDBModel,
    TimeEntryCosmosDBRepository,
)

from time_tracker_api.projects.projects_model import (
    ProjectCosmosDBDao,
    ProjectCosmosDBModel,
)
from time_tracker_api.activities.activities_model import (
    ActivityCosmosDBDao,
    ActivityCosmosDBModel,
)

time_entry_data = {
    'id': 'id',
    'start_date': '2021-03-22T10:00:00.000Z',
    'end_date': "2021-03-22T11:00:00.000Z",
    'description': 'do some testing',
    'tenant_id': 'tenant_id',
    'project_id': 'project_id1',
    'activity_id': 'activity_id1',
    'technologies': ['python', 'pytest'],
    'owner_id': 'id',
}

project_data = {
    'customer_id': 'dsakldh12ASD',
    'id': 'project_id1',
    'name': 'project_name',
    'description': 'do some testing',
    'project_type_id': "id2",
    'tenant_id': 'tenantid1',
}

activity_data = {
    'id': 'activity_id1',
    'name': 'activity',
    'description': 'testing',
    "tenant_id": 'nomatter',
}


def test_add_complementary_info(
    mocker,
    time_entry_repository: TimeEntryCosmosDBRepository,
):
    projects_db_get_all_mock = mocker.patch.object(
        ProjectCosmosDBDao, 'get_all'
    )
    activities_db_get_all_mock = mocker.patch.object(
        ActivityCosmosDBDao, 'get_all'
    )
    users_mock = mocker.patch.object(AzureConnection, 'users')

    expected_project = ProjectCosmosDBModel(project_data)
    expected_activity = ActivityCosmosDBModel(activity_data)
    expected_time_entry_in = TimeEntryCosmosDBModel(time_entry_data)
    expected_user = AzureUser('email1', [], 'id', 'name', ['admin'])
    setattr(expected_project, 'customer_name', 'customer_name')

    projects_db_get_all_mock.return_value = [expected_project]
    activities_db_get_all_mock.return_value = [expected_activity]
    users_mock.return_value = [expected_user]

    expected_time_entry_out = time_entry_repository.add_complementary_info(
        [expected_time_entry_in], max_count=None, exist_conditions=True
    )

    assert isinstance(expected_time_entry_out[0], TimeEntryCosmosDBModel)
    assert (
        expected_time_entry_out[0].__dict__['project_name']
        == expected_project.__dict__['name']
    )
    assert (
        expected_time_entry_out[0].__dict__['customer_id']
        == expected_project.__dict__['customer_id']
    )
    assert (
        expected_time_entry_out[0].__dict__['customer_name']
        == expected_project.__dict__['customer_name']
    )
    assert (
        expected_time_entry_out[0].__dict__['activity_name']
        == expected_activity.__dict__['name']
    )
