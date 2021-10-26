from dataclasses import dataclass


@dataclass(frozen=True)
class Activity:
    id: str
    name: str
    description: str
    deleted: str
    status: str
    tenant_id: str
