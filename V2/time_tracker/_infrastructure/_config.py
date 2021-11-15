import typing
import os

CONNECTION_STRING = 'postgresql://root:root@localhost:5433/timetracker'


class Config(typing.NamedTuple):
    DB_CONNECTION_STRING: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str


def load_config():
    return Config(
        CONNECTION_STRING if os.environ.get("DB_CONNECTION_STRING") is None else os.environ.get("DB_CONNECTION_STRING"),
        os.environ.get("DB_USER"),
        os.environ.get("DB_PASS"),
        os.environ.get("DB_NAME")
    )
