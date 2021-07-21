from enum import Enum


class TimeTrackerEntities(Enum):
    def __str__(self):
        return str(self.value)

    CUSTOMER = 'Customers'
    PROJECT = 'Projects'
    PROJECT_TYPE = 'Project-Types'
    ACTIVITY = 'Activities'
    TIME_ENTRY = 'Time-entries'
