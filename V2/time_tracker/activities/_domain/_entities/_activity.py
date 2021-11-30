import typing

from dataclasses import dataclass


@dataclass(frozen=True)
class Activity:
    id: typing.Optional[int]
    name: str
    description: str
    deleted: typing.Optional[bool]
    status: typing.Optional[int]
