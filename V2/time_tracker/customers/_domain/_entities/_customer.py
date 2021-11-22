from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    id: int
    name: str
    description: str
    deleted: bool
    status: int
