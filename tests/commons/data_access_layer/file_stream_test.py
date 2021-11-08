import json

from commons.data_access_layer.file_stream import FileStream

fs = FileStream("storagefiles2","ioetfiles")

def test_get_file_stream_return_file_when_enter_file_name():
    result = fs.get_file_stream("activity.json")
  
    assert len(json.load(result)) == 15

def test_get_file_stream_return_None_when_not_enter_file_name_or_incorrect_name():
    result = fs.get_file_stream("")
  
    assert result == None