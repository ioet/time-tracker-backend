def convert_list_to_tuple_string(id_list):
    validate_list(id_list)
    id_value = (
        f"('{id_list[0]}')" if len(id_list) == 1 else str(tuple(id_list))
    )
    return id_value


def validate_list(id_list):
    assert isinstance(id_list, list)
    assert len(id_list) > 0
