from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Project:
    id: Optional[int]
    name: str
    description: str
    project_type_id: int
    customer_id: int
    status: int
    deleted: Optional[bool]
    technologies: List[str]

    customer: Optional[dict]
