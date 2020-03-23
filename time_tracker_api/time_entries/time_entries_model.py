from flask import Flask

from time_tracker_api.database import CRUDDao


class TimeEntriesDao(CRUDDao):
    pass


def create_dao(app: Flask) -> TimeEntriesDao:
    # TODO Create implementation(s)
    return TimeEntriesDao()
