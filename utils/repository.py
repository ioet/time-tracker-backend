def convert_list_to_tuple_string(ids_list):
    assert isinstance(ids_list, list)
    assert len(ids_list) > 0
    result = (
        str(tuple(ids_list)).replace(",", "")
        if len(ids_list) == 1
        else str(tuple(ids_list))
    )
    return result


def create_sql_in_condition(field, values):
    tuple_string = convert_list_to_tuple_string(values)

    return "c.{field} IN {list}".format(field=field, list=tuple_string)


def get_string_without_empty_spaces(string: str):
    from re import sub

    string = string.replace("\n", "")
    return sub("[\s]+", ' ', string).rstrip().lstrip()
