from dataclasses import dataclass
import typing


@dataclass(frozen=True)
class Customer:
    id: typing.Optional[int]
    name: str
    description: str
    deleted: typing.Optional[bool]
    status: typing.Optional[int]
