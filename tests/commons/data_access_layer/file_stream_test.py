import json
import pytest

from commons.data_access_layer.file import FileStream

fs = FileStream("tt-common-files")

@pytest.mark.skip(reason='file not in the repository')

def test__get_file_stream__return_file_content__when_enter_file_name():
    result = fs.get_file_stream("activity_test.json")

    assert len(json.loads(result)) == 15


def test__get_file_stream__return_None__when_not_enter_file_name_or_incorrect_name():
    result = fs.get_file_stream("")

    assert result == None
