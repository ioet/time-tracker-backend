import typing
import os

CONNECTION_STRING = 'postgresql://root:root@localhost:5433/timetracker'


class Config(typing.NamedTuple):
    DB_CONNECTION_STRING: str


def load_config():
    if os.environ.get("ENVIRONMENT") == "development":
        connection: str = os.environ.get("DB_CONNECTION")
    else:
        connection: str = os.environ.get("TEST_DB_CONNECTION")

    return Config(
         CONNECTION_STRING if connection is None else connection
    )
