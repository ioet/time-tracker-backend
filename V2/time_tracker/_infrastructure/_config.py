import typing
import os


class Config(typing.NamedTuple):
    DB_CONNECTION_STRING: str


def load_config():
    if os.environ.get("ENVIRONMENT") == "development":
        connection: str = os.environ.get("DB_CONNECTION")
    else:
        connection: str = os.environ.get("TEST_DB_CONNECTION")

    return Config(
      connection
    )
