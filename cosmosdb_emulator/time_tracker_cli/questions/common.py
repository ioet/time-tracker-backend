from PyInquirer import prompt

from cosmosdb_emulator.time_tracker_cli.enums.entites import (
    TimeTrackerEntities,
)
from cosmosdb_emulator.time_tracker_cli.utils.common import (
    stop_execution_if_user_input_is_invalid,
)


time_tracker_entities = [entity.value for entity in TimeTrackerEntities]

entities_actions = ['Create', 'Delete']


def ask_entity(action: str):
    question_key = 'entity'

    select_entity_question = {
        'type': 'list',
        'name': question_key,
        'message': f'Perfect, please provide the entity that you want to {action.lower()}:',
        'choices': time_tracker_entities,
    }

    selected_entity_answer = prompt(select_entity_question)
    selected_entity = selected_entity_answer.get(question_key)
    stop_execution_if_user_input_is_invalid(selected_entity)

    return selected_entity


def ask_action():
    question_key = 'action'

    select_action_question = {
        'type': 'list',
        'name': question_key,
        'message': 'Hello TT Coder, what action do you want to generate on the entities?',
        'choices': entities_actions,
    }

    selected_action_answer = prompt(select_action_question)
    selected_action = selected_action_answer.get(question_key)
    stop_execution_if_user_input_is_invalid(selected_action)

    return selected_action


def ask_delete_confirmation(entities_to_eliminate: set) -> bool:
    question_key = 'delete_confirmation'

    join_element = ', '
    entities = join_element.join(entities_to_eliminate)

    message = f'Are you sure to delete these ({entities}) entities'

    delete_confirmation_question = {
        'type': 'confirm',
        'name': question_key,
        'message': message,
        'default': True,
    }

    delete_confirmation_answer = prompt(delete_confirmation_question)
    is_user_agree_to_delete = delete_confirmation_answer.get(question_key)
    stop_execution_if_user_input_is_invalid(is_user_agree_to_delete)

    return is_user_agree_to_delete
