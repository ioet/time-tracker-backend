def convert_list_to_tuple_string(ids_list):
    assert isinstance(ids_list, list)
    assert len(ids_list) > 0
    result = (
        str(tuple(ids_list)).replace(",", "")
        if len(ids_list) == 1
        else str(tuple(ids_list))
    )
    return result


def get_string_without_empty_spaces(string: str):
    from re import sub

    string = string.replace("\n", "")
    return sub("[\s]+", ' ', string).rstrip().lstrip()
