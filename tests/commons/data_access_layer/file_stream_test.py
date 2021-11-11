import json

from commons.data_access_layer.file_stream import FileStream

fs = FileStream("storageaccounteystr82c5","tt-common-files")

def test__get_file_stream__return_file_content__when_enter_file_name():
    result = fs.get_file_stream("activity_test.json")
  
    assert len(json.load(result)) == 15

def test__get_file_stream__return_None__when_not_enter_file_name_or_incorrect_name():
    result = fs.get_file_stream("")
  
    assert result == None