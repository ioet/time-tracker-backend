from V2.source import use_cases
from V2.source.daos.activities_json_dao import ActivitiesJsonDao
import pytest

@pytest.fixture(scope='module')
def activities_json_dao():
    activities_json_dao = ActivitiesJsonDao('./V2/source/activities_data.json')
    return activities_json_dao

def test_get_activities_use_case(activities_json_dao):
    activities_dto = activities_json_dao.get_all()
    activities_expected = use_cases.get_list_activities()

    assert activities_dto == activities_expected

def test_get_activity_by_id_use_case(activities_json_dao):
    activity_dto = activities_json_dao.get_by_id('94ec92e2-a500-4700-a9f6-e41eb7b5507c')
    activity_expected = use_cases.get_activity_by_id('94ec92e2-a500-4700-a9f6-e41eb7b5507c')

    assert activity_dto == activity_expected