from time_tracker.utils.enums import StatusEnums


def parse_status_to_string_for_ui(activity: dict) -> dict:
    activity['status'] = StatusEnums(activity['status']).name
    return activity


def parse_status_to_number(status: str) -> int:
    if(isinstance(status, str)):
        return StatusEnums[status].value
    return status
