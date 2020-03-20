from faker import Faker

fake = Faker()

existing_elements_registry = []
last_deleted_element = None


def test_create(sql_repository):
    global sample_element
    sample_element = dict(name=fake.name(),
                          email=fake.safe_email(),
                          age=fake.pyint(min_value=10, max_value=80))

    result = sql_repository.create(sample_element)

    assert result is not None
    assert result.id is not None
    assert result.created_at is not None
    assert result.created_by is not None
    assert result.updated_at is None
    assert result.updated_by is None

    existing_elements_registry.append(result)


def test_find(sql_repository):
    existing_element = existing_elements_registry[0]

    found_element = sql_repository.find(existing_element.id)

    assert found_element is not None
    assert found_element.id is not None


def test_update(sql_repository):
    existing_element = existing_elements_registry[0]

    updated_element = sql_repository.update(existing_element.id,
                                            dict(name="Jon Snow", age=34))

    assert updated_element is not None
    assert updated_element.id == existing_element.id
    assert updated_element.name == "Jon Snow"
    assert updated_element.age == 34
    assert updated_element.updated_at is not None
    assert updated_element.updated_at > updated_element.created_at
    assert updated_element.updated_by is not None


def test_find_all(sql_repository):
    existing_elements = sql_repository.find_all()

    assert all(e in existing_elements_registry for e in existing_elements)


def test_find_all_that_contains_property_with_string(sql_repository):
    """Find all elements that have a property that partially contains a string (case-insensitive)"""
    fake_name = fake.name()
    new_element = dict(name="%s Snow" % fake_name,
                       email=fake.safe_email(),
                       age=fake.pyint(min_value=10, max_value=80))
    sql_repository.create(new_element)
    existing_elements_registry.append(new_element)

    search_snow_result = sql_repository.find_all_contain_str('name', 'Snow')
    assert len(search_snow_result) == 2

    search_jon_result = sql_repository.find_all_contain_str('name', 'Jon')
    assert len(search_jon_result) == 1

    search_ram_result = sql_repository.find_all_contain_str('name', fake_name)
    assert search_ram_result[0].name == new_element['name']


def test_delete_existing_element(sql_repository):
    existing_element = existing_elements_registry[0]

    result = sql_repository.remove(existing_element.id)

    assert result is None

    global last_deleted_model
    last_deleted_model = existing_elements_registry.pop()
