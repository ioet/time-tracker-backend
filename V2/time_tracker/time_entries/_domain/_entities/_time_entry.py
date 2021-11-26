from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class TimeEntry:
    id: Optional[int]
    start_date: str
    owner_id: int
    description: str
    activity_id: int
    uri: str
    technologies: List[str]
    end_date: str
    deleted: Optional[bool]
    timezone_offset: str
    project_id: int
