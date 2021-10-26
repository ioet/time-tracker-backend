import json
import pytest
import shutil


@pytest.fixture
def create_temp_activities(tmpdir_factory):
    temporary_directory = tmpdir_factory.mktemp("tmp")
    json_file = temporary_directory.join("activities.json")
    activities = [
        {
            'id': 'c61a4a49-3364-49a3-a7f7-0c5f2d15072b',
            'name': 'Development',
            'description': 'Development',
            'deleted': 'b4327ba6-9f96-49ee-a9ac-3c1edf525172',
            'status': 'active',
            'tenant_id': 'cc925a5d-9644-4a4f-8d99-0bee49aadd05',
        },
        {
            'id': '94ec92e2-a500-4700-a9f6-e41eb7b5507c',
            'name': 'Management',
            'description': 'Description of management',
            'deleted': '7cf6efe5-a221-4fe4-b94f-8945127a489a',
            'status': 'active',
            'tenant_id': 'cc925a5d-9644-4a4f-8d99-0bee49aadd05',
        },
        {
            'id': 'd45c770a-b1a0-4bd8-a713-22c01a23e41b',
            'name': 'Operations',
            'description': 'Operation activities performed.',
            'deleted': '7cf6efe5-a221-4fe4-b94f-8945127a489a',
            'status': 'active',
            'tenant_id': 'cc925a5d-9644-4a4f-8d99-0bee49aadd05',
        },
    ]

    with open(json_file, 'w') as outfile:
        json.dump(activities, outfile)

    yield activities, json_file
    shutil.rmtree(temporary_directory)
