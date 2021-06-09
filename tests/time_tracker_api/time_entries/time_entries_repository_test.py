from utils.extend_model import (
    add_project_info_to_time_entries,
    add_activity_name_to_time_entries,
)
from time_tracker_api.time_entries.time_entries_repository import (
    TimeEntryCosmosDBModel,
)
from time_tracker_api.time_entries.time_entries_dao import (
    TimeEntriesCosmosDBDao,
)
from time_tracker_api.projects.projects_model import (
    ProjectCosmosDBDao,
    ProjectCosmosDBModel,
)
from time_tracker_api.activities.activities_model import (
    ActivityCosmosDBDao,
    ActivityCosmosDBModel,
)


def test_add_complementary_info(
    mocker,
):
    time_entry_data = {
        'id': 'id',
        'start_date': '2021-03-22T10:00:00.000Z',
        'end_date': "2021-03-22T11:00:00.000Z",
        'description': 'do some testing',
        'tenant_id': 'tenant_id',
        'project_id': 'project_id1',
        'activity_id': 'activity_id1',
        'technologies': ['python', 'pytest'],
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
    projects_db_get_all_mock = mocker.patch.object(
        ProjectCosmosDBDao, 'get_all'
    )
    activities_db_get_all_mock = mocker.patch.object(
        ActivityCosmosDBDao, 'get_all'
    )
    time_entry_db_get_all_mock = mocker.patch.object(
        TimeEntriesCosmosDBDao, 'get_all'
    )

    expected_projects = ProjectCosmosDBModel(project_data)
    expected_activities = ActivityCosmosDBModel(activity_data)
    expected_time_entry = TimeEntryCosmosDBModel(time_entry_data)
    setattr(expected_projects, 'customer_name', 'customer_name')

    projects_db_get_all_mock.return_value = expected_projects
    activities_db_get_all_mock.return_value = expected_activities
    time_entry_db_get_all_mock.return_value = expected_time_entry

    add_project_info_to_time_entries(
        [expected_time_entry], [expected_projects]
    )
    add_activity_name_to_time_entries(
        [expected_time_entry], [expected_activities]
    )

    assert (
        expected_time_entry.__dict__['project_name']
        == expected_projects.__dict__['name']
    )
    assert (
        expected_time_entry.__dict__['customer_id']
        == expected_projects.__dict__['customer_id']
    )
    assert (
        expected_time_entry.__dict__['customer_name']
        == expected_projects.__dict__['customer_name']
    )
    assert (
        expected_time_entry.__dict__['activity_name']
        == expected_activities.__dict__['name']
    )
