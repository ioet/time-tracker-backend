from PyInquirer import Separator, prompt

from cosmosdb_emulator.time_tracker_cli.utils.common import (
    stop_execution_if_user_input_is_invalid,
)
from cosmosdb_emulator.time_tracker_cli.validators.max_amount import (
    MaxAmountValidator,
)
from cosmosdb_emulator.time_tracker_cli.validators.number import (
    NumberValidator,
)
from cosmosdb_emulator.time_tracker_cli.validators.uuid import UUIDValidator


def ask_delete_entries():
    question_key = 'delete'
    delete_entries_question = {
        'type': 'confirm',
        'name': question_key,
        'message': (
            'We are going to delete all entries that is currently in the emulator, are you sure to continue?'
        ),
        'default': True,
    }

    delete_data_answer = prompt(delete_entries_question)
    user_agree_to_delete_data = delete_data_answer.get(question_key)
    stop_execution_if_user_input_is_invalid(user_agree_to_delete_data)
    return user_agree_to_delete_data


def ask_entry_type():
    question_key = 'entry_type'
    entry_type_question = {
        'type': 'list',
        'name': question_key,
        'message': 'What type of entry do you want to generate?',
        'choices': [
            Separator('<=== AVAILABLE ENTRY TYPES ====>'),
            {'name': 'Own entries (Time Entries Page)', 'value': 'OE'},
            {'name': 'General entries (Reports Page)', 'value': 'GE'},
        ],
    }
    entry_type_answer = prompt(entry_type_question)
    entry_type = entry_type_answer.get('entry_type')
    stop_execution_if_user_input_is_invalid(entry_type)
    return entry_type


def ask_entries_amount(entries_type: str):
    question_key = 'entries_amount'
    message_for_own_entries = 'Enter the amount of entries that you need:'
    message_for_general_entries = (
        'Enter the amount of entries per user that you need:'
    )
    own_entries_id = 'OE'

    entries_amount_message = (
        message_for_own_entries
        if entries_type == own_entries_id
        else message_for_general_entries
    )

    entries_amount_question = {
        'type': 'input',
        'name': question_key,
        'message': entries_amount_message,
        'validate': NumberValidator,
    }

    entries_amount_answer = prompt(entries_amount_question).get(question_key)
    stop_execution_if_user_input_is_invalid(entries_amount_answer)
    entries_amount = int(entries_amount_answer)
    return entries_amount


def ask_user_identifier() -> str:
    question_key = 'user_id'
    user_identifier_question = {
        'type': 'input',
        'name': question_key,
        'message': 'Please your identifier:',
        'validate': UUIDValidator,
    }
    user_identifier_answer = prompt(user_identifier_question)
    user_identifier = user_identifier_answer.get(question_key)
    stop_execution_if_user_input_is_invalid(user_identifier)
    return user_identifier


def ask_entries_owners_amount(users_amount: int) -> int:
    question_key = 'entries_owners_amount'
    entries_owners_amount_question = {
        'type': 'input',
        'name': question_key,
        'message': 'Enter the number of users to be assigned entries:',
    }

    max_amount_validator = MaxAmountValidator(
        max_amount=users_amount,
        error_message='We do not have that amount of users, do not be smart!',
    )

    entries_owners_amount_answer = prompt(
        entries_owners_amount_question, validator=max_amount_validator
    ).get(question_key)
    stop_execution_if_user_input_is_invalid(entries_owners_amount_answer)
    return int(entries_owners_amount_answer)
