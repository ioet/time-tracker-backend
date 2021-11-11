from dataclasses import dataclass


@dataclass(frozen=True)
class Activity:
    id: int
    name: str
    description: str
    deleted: bool
    status: int
