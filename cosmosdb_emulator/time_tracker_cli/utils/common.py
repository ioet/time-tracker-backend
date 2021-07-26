import sys
from typing import List

from faker import Faker


def get_time_tracker_tenant_id() -> str:
    """
    This tenant id is necessary for all factories, use this value in
    the field tenant_id of all factories
    """
    time_tracker_tenant_id = 'cc925a5d-9644-4a4f-8d99-0bee49aadd05'
    return time_tracker_tenant_id


def stop_execution_if_user_input_is_invalid(user_input: str):
    if user_input is None:
        print('Thanks for coming, see you later!')
        sys.exit()


def get_unique_elements_from_list(elements_list, amount_of_elements) -> List:
    entry_owners = Faker().random_elements(
        elements=elements_list, length=amount_of_elements, unique=True
    )
    return entry_owners


def get_random_element_from_list(elements_list):
    random_element = Faker().random_element(elements=elements_list)
    return random_element
