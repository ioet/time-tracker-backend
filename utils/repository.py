def convert_list_to_tuple_string(ids_list):
    validate_list(ids_list)
    id_value = (
        str(tuple(ids_list)).replace(",", "")
        if len(ids_list) == 1
        else str(tuple(ids_list))
    )
    return id_value


def validate_list(ids_list):
    assert isinstance(ids_list, list)
    assert len(ids_list) > 0
