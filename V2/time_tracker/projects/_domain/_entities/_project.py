from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    description: str
    project_type_id: int
    customer_id: int
    status: int
    deleted: bool