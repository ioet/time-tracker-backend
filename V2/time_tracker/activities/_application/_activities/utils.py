from time_tracker.utils.enums import StatusEnums


def parse_status_to_string_for_ui(activity: dict) -> dict:
    activity['status'] = StatusEnums(activity['status']).name
    return activity
