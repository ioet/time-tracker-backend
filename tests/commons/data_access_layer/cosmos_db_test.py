from dataclasses import dataclass
from typing import Callable

import pytest
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
from faker import Faker
from flask_restplus._http import HTTPStatus
from pytest import fail

from commons.data_access_layer.cosmos_db import CosmosDBRepository, CosmosDBModel, CustomError

fake = Faker()
Faker.seed()

existing_item: dict = None


@dataclass()
class Person(CosmosDBModel):
    id: str
    name: str
    email: str
    age: int
    tenant_id: str

    def __init__(self, data):
        super(Person, self).__init__(data)

    def is_adult(self):
        return self.age >= 18


def test_repository_exists(cosmos_db_repository):
    assert cosmos_db_repository is not None


def test_create_should_succeed(cosmos_db_repository: CosmosDBRepository, tenant_id: str):
    global existing_item
    existing_item = dict(id=fake.uuid4(),
                         name=fake.name(),
                         email=fake.safe_email(),
                         age=fake.pyint(min_value=10, max_value=80),
                         tenant_id=tenant_id)

    created_item = cosmos_db_repository.create(existing_item)

    assert created_item is not None
    assert all(item in created_item.items() for item in existing_item.items())


def test_create_should_fail_if_user_is_same(cosmos_db_repository: CosmosDBRepository):
    try:
        global existing_elemen
        cosmos_db_repository.create(existing_item)

        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceExistsError
        assert e.status_code == 409


def test_create_with_diff_unique_data_but_same_tenant_should_succeed(
        cosmos_db_repository: CosmosDBRepository):
    global existing_item
    new_data = existing_item.copy()
    new_data.update({
        'id': fake.uuid4(),
        'email': fake.safe_email(),
    })

    result = cosmos_db_repository.create(new_data)
    assert result["id"] != existing_item["id"], 'It should be a new element'


def test_create_with_same_id_should_fail(
        cosmos_db_repository: CosmosDBRepository):
    try:
        global existing_item
        new_data = existing_item.copy()
        new_data.update({
            'email': fake.safe_email(),
        })

        cosmos_db_repository.create(new_data)

        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceExistsError
        assert e.status_code == 409


def test_create_with_diff_id_but_same_unique_field_should_fail(
        cosmos_db_repository: CosmosDBRepository):
    try:
        global existing_item
        new_data = existing_item.copy()
        new_data.update({
            'id': fake.uuid4()
        })

        cosmos_db_repository.create(new_data)

        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceExistsError
        assert e.status_code == 409


def test_create_with_no_partition_key_attrib_should_pass(
        cosmos_db_repository: CosmosDBRepository):
    global existing_item
    new_data = existing_item.copy()

    new_data.update({
        'tenant_id': None,
    })

    result = cosmos_db_repository.create(new_data)
    assert result["tenant_id"] is None, "A None value in a partition key is valid"


def test_create_with_same_id_but_diff_partition_key_attrib_should_succeed(
        cosmos_db_repository: CosmosDBRepository,
        another_tenant_id: str):
    global existing_item
    new_data = existing_item.copy()

    new_data.update({
        'tenant_id': another_tenant_id,
    })

    result = cosmos_db_repository.create(new_data)
    assert result["id"] == existing_item["id"], "Should have allowed same id"


def test_create_with_mapper_should_provide_calculated_fields(
        cosmos_db_repository: CosmosDBRepository, tenant_id):
    new_item = dict(id=fake.uuid4(),
                    name=fake.name(),
                    email=fake.safe_email(),
                    age=fake.pyint(min_value=10, max_value=80),
                    tenant_id=tenant_id)

    created_item: Person = cosmos_db_repository.create(new_item, mapper=Person)

    assert created_item is not None
    assert all(item in created_item.__dict__.items() for item in new_item.items())
    assert type(created_item) is Person, "The result should be wrapped with a class"
    assert created_item.is_adult() is (new_item["age"] >= 18)


def test_find_by_valid_id_should_succeed(cosmos_db_repository: CosmosDBRepository):
    found_item = cosmos_db_repository.find(existing_item["id"],
                                           existing_item['tenant_id'])

    assert all(item in found_item.items() for item in existing_item.items())


def test_find_by_invalid_id_should_fail(cosmos_db_repository: CosmosDBRepository):
    try:
        cosmos_db_repository.find(fake.uuid4(), existing_item['tenant_id'])

        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_find_by_invalid_partition_key_value_should_fail(cosmos_db_repository: CosmosDBRepository):
    try:
        cosmos_db_repository.find(existing_item["id"], fake.uuid4())

        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_find_by_valid_id_and_mapper_should_succeed(cosmos_db_repository: CosmosDBRepository):
    found_item: Person = cosmos_db_repository.find(existing_item["id"],
                                                   existing_item['tenant_id'],
                                                   mapper=Person)

    assert all(item in found_item.__dict__.items() for item in existing_item.items())
    assert type(found_item) is Person, "The result should be wrapped with a class"
    assert found_item.is_adult() is (existing_item["age"] >= 18)


@pytest.mark.parametrize(
    'mapper,expected_type', [(None, dict), (dict, dict), (Person, Person)]
)
def test_find_all_with_mapper(cosmos_db_repository: CosmosDBRepository,
                              tenant_id: str,
                              mapper: Callable,
                              expected_type: Callable):
    result = cosmos_db_repository.find_all(tenant_id, mapper=mapper)

    assert result is not None
    assert len(result) > 0
    assert type(result[0]) is expected_type, "The result type is not the expected"


def test_find_all_should_return_items_from_specified_partition_key_value(
        cosmos_db_repository: CosmosDBRepository,
        tenant_id: str,
        another_tenant_id: str):
    result_tenant_id = cosmos_db_repository.find_all(tenant_id)

    assert len(result_tenant_id) > 1
    assert all((i["tenant_id"] == tenant_id for i in result_tenant_id))

    result_another_tenant_id = cosmos_db_repository.find_all(another_tenant_id)

    assert len(result_another_tenant_id) > 0
    assert all((i["tenant_id"] == another_tenant_id for i in result_another_tenant_id))

    assert not any(item in result_another_tenant_id for item in result_tenant_id), \
        "There should be no interceptions"


def test_find_all_should_succeed_with_partition_key_value_with_no_items(
        cosmos_db_repository: CosmosDBRepository):
    no_items = cosmos_db_repository.find_all(fake.uuid4())

    assert no_items is not None
    assert len(no_items) == 0, "No items are expected"


def test_find_all_with_max_count(cosmos_db_repository: CosmosDBRepository,
                                 tenant_id: str):
    all_items = cosmos_db_repository.find_all(tenant_id)

    assert len(all_items) > 2

    first_two_items = cosmos_db_repository.find_all(tenant_id, max_count=2)
    assert len(first_two_items) == 2, "The result should be limited to 2"


def test_find_all_with_offset(cosmos_db_repository: CosmosDBRepository,
                              tenant_id: str):
    result_all_items = cosmos_db_repository.find_all(tenant_id)

    assert len(result_all_items) >= 3

    result_after_the_first_item = cosmos_db_repository.find_all(tenant_id, offset=1)

    assert result_after_the_first_item == result_all_items[1:]

    result_after_the_second_item = cosmos_db_repository.find_all(tenant_id, offset=2)

    assert result_after_the_second_item == result_all_items[2:]


@pytest.mark.parametrize(
    'mapper,expected_type', [(None, dict), (dict, dict), (Person, Person)]
)
def test_partial_update_with_mapper(cosmos_db_repository: CosmosDBRepository,
                                    mapper: Callable,
                                    expected_type: Callable):
    changes = {
        'name': fake.name(),
        'email': fake.safe_email(),
    }

    updated_item = cosmos_db_repository.partial_update(existing_item['id'],
                                                       changes,
                                                       existing_item['tenant_id'],
                                                       mapper=mapper)

    assert updated_item is not None
    assert type(updated_item) is expected_type


def test_partial_update_with_new_partition_key_value_should_fail(
        cosmos_db_repository: CosmosDBRepository,
        another_tenant_id: str,
        sample_item: dict):
    changes = {
        'name': fake.name(),
        'email': fake.safe_email(),
    }

    try:
        cosmos_db_repository.partial_update(sample_item['id'], changes, another_tenant_id)
        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_partial_update_with_invalid_id_should_fail(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    changes = {
        'name': fake.name(),
        'email': fake.safe_email(),
    }

    try:
        cosmos_db_repository.partial_update(fake.uuid4(), changes, sample_item['tenant_id'])
        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_partial_update_should_only_update_fields_in_changes(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    changes = {
        'name': fake.name(),
        'email': fake.safe_email(),
    }

    updated_item = cosmos_db_repository.partial_update(
        sample_item['id'],
        changes, sample_item['tenant_id'])

    assert updated_item is not None
    assert updated_item['name'] == changes["name"] != sample_item["name"]
    assert updated_item['email'] == changes["email"] != sample_item["email"]
    assert updated_item['id'] == sample_item["id"]
    assert updated_item['tenant_id'] == sample_item["tenant_id"]
    assert updated_item['age'] == sample_item["age"]


@pytest.mark.parametrize(
    'mapper,expected_type', [(None, dict), (dict, dict), (Person, Person)]
)
def test_update_with_mapper(cosmos_db_repository: CosmosDBRepository,
                            mapper: Callable,
                            expected_type: Callable):
    changed_item = existing_item.copy()
    changed_item.update({
        'name': fake.name(),
        'email': fake.safe_email(),
    })

    updated_item = cosmos_db_repository.update(existing_item['id'],
                                               changed_item,
                                               mapper=mapper)

    assert updated_item is not None
    assert type(updated_item) is expected_type


def test_update_with_invalid_id_should_fail(cosmos_db_repository: CosmosDBRepository):
    changes = {
        'name': fake.name(),
        'email': fake.safe_email(),
    }

    try:
        cosmos_db_repository.update(fake.uuid4(), changes)
        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_update_with_partial_changes_without_required_fields_it_should_fail(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    changes = {
        'id': sample_item['id'],
        'email': fake.safe_email(),
        'tenant_id': fake.uuid4(),
    }

    try:
        cosmos_db_repository.update(sample_item['id'], changes)
        fail('It should have failed')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_update_with_partial_changes_with_required_fields_should_delete_the_missing_ones(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    changes = {
        'id': fake.uuid4(),
        'email': fake.safe_email(),
        'tenant_id': sample_item['tenant_id'],
    }

    updated_item = cosmos_db_repository.update(sample_item['id'], changes)

    assert updated_item is not None
    assert updated_item['id'] == changes["id"] != sample_item["id"]
    assert updated_item['email'] == changes["email"] != sample_item["email"]
    assert updated_item['tenant_id'] == changes["tenant_id"]
    assert updated_item.get('name') is None
    assert updated_item.get('age') is None

    try:
        cosmos_db_repository.find(sample_item['id'], sample_item['tenant_id'])
        fail('The previous version should not exist')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_delete_with_invalid_id_should_fail(cosmos_db_repository: CosmosDBRepository,
                                            tenant_id: str):
    try:
        cosmos_db_repository.delete(fake.uuid4(), tenant_id)
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


@pytest.mark.parametrize(
    'mapper,expected_type', [(None, dict), (dict, dict), (Person, Person)]
)
def test_delete_with_mapper(cosmos_db_repository: CosmosDBRepository,
                            sample_item: dict,
                            mapper: Callable,
                            expected_type: Callable):
    deleted_item = cosmos_db_repository.delete(sample_item['id'],
                                               sample_item['tenant_id'],
                                               mapper=mapper)

    assert deleted_item is not None
    assert type(deleted_item) is expected_type

    try:
        cosmos_db_repository.find(sample_item['id'],
                                  sample_item['tenant_id'],
                                  mapper=mapper)
        fail('It should have not found the deleted item')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_find_can_find_deleted_item_only_if_visibile_only_is_true(cosmos_db_repository: CosmosDBRepository,
                                                                  sample_item: dict):
    deleted_item = cosmos_db_repository.delete(sample_item['id'], sample_item['tenant_id'])

    assert deleted_item is not None
    assert deleted_item['deleted'] is not None

    try:
        cosmos_db_repository.find(sample_item['id'], sample_item['tenant_id'])
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404

    found_deleted_item = cosmos_db_repository.find(sample_item['id'],
                                                   sample_item['tenant_id'],
                                                   visible_only=False)
    assert found_deleted_item is not None


def test_find_all_can_find_deleted_items_only_if_visibile_only_is_true(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    deleted_item = cosmos_db_repository.delete(sample_item['id'], sample_item['tenant_id'])
    assert deleted_item is not None
    assert deleted_item['deleted'] is not None

    visible_items = cosmos_db_repository.find_all(partition_key_value=sample_item.get('tenant_id'))

    assert visible_items is not None
    assert any(item['id'] == sample_item['id'] for item in visible_items) == False, \
        'The deleted item should not be visible'

    all_items = cosmos_db_repository.find_all(sample_item['tenant_id'], visible_only=False)

    assert all_items is not None
    assert any(item['id'] == sample_item['id'] for item in all_items), \
        'Deleted item should be visible'


def test_delete_should_not_find_element_that_is_already_deleted(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    deleted_item = cosmos_db_repository.delete(sample_item['id'], sample_item['tenant_id'])

    assert deleted_item is not None

    try:
        cosmos_db_repository.delete(deleted_item['id'], deleted_item['tenant_id'])
        fail('It should have not found the deleted item')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_partial_update_should_not_find_element_that_is_already_deleted(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    deleted_item = cosmos_db_repository.delete(sample_item['id'], sample_item['tenant_id'])

    assert deleted_item is not None

    try:
        changes = {
            'name': fake.name(),
            'email': fake.safe_email(),
        }
        cosmos_db_repository.partial_update(deleted_item['id'],
                                            changes,
                                            deleted_item['tenant_id'])

        fail('It should have not found the deleted item')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_delete_permanently_with_invalid_id_should_fail(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    try:
        cosmos_db_repository.delete_permanently(fake.uuid4(), sample_item['tenant_id'])
        fail('It should have not found the deleted item')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_delete_permanently_with_valid_id_should_succeed(
        cosmos_db_repository: CosmosDBRepository,
        sample_item: dict):
    found_item = cosmos_db_repository.find(sample_item['id'], sample_item['tenant_id'])

    assert found_item is not None
    assert found_item['id'] == sample_item['id']

    cosmos_db_repository.delete_permanently(sample_item['id'], sample_item['tenant_id'])

    try:
        cosmos_db_repository.find(sample_item['id'], sample_item['tenant_id'])
        fail('It should have not found the deleted item')
    except Exception as e:
        assert type(e) is CosmosResourceNotFoundError
        assert e.status_code == 404


def test_repository_create_sql_where_conditions_with_multiple_values(cosmos_db_repository: CosmosDBRepository):
    result = cosmos_db_repository.create_sql_where_conditions({
        'owner_id': 'mark',
        'customer_id': 'me'
    }, "c")

    assert result is not None
    assert result == "AND c.owner_id = @owner_id AND c.customer_id = @customer_id"


def test_repository_create_sql_where_conditions_with_no_values(cosmos_db_repository: CosmosDBRepository):
    result = cosmos_db_repository.create_sql_where_conditions({}, "c")

    assert result is not None
    assert result == ""


def test_repository_append_conditions_values(cosmos_db_repository: CosmosDBRepository):
    result = cosmos_db_repository.append_conditions_values([], {'owner_id': 'mark', 'customer_id': 'ioet'})

    assert result is not None
    assert result == [{'name': '@owner_id', 'value': 'mark'},
                      {'name': '@customer_id', 'value': 'ioet'}]


def test_find_should_call_picker_if_it_was_specified(cosmos_db_repository: CosmosDBRepository,
                                                     sample_item: dict,
                                                     another_item: dict):
    def raise_bad_request_if_name_diff_the_one_from_sample_item(data: dict):
        if sample_item['name'] != data['name']:
            raise CustomError(HTTPStatus.BAD_REQUEST, "Anything")

    found_item = cosmos_db_repository.find(sample_item['id'],
                                           partition_key_value=sample_item['tenant_id'])

    assert found_item is not None
    assert found_item['id'] == sample_item['id']

    try:
        cosmos_db_repository.find(another_item['id'],
                                  partition_key_value=another_item['tenant_id'],
                                  peeker=raise_bad_request_if_name_diff_the_one_from_sample_item)

        fail('It should have not found any item because of condition')
    except Exception as e:
        assert e.code == HTTPStatus.BAD_REQUEST
        assert e.description == "Anything"
