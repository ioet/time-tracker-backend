import typing
import os

class Config(typing.NamedTuple):
    DB_CONNECTION_STRING: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str


def load_config():
    return Config(os.environ.get("DB_CONNECTION_STRING"),os.environ.get("DB_USER"),os.environ.get("DB_PASS"),os.environ.get("DB_NAME"))