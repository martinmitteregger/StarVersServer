from datetime import datetime
from typing import List
from uuid import UUID
from app.enums.DeltaTypeEnum import DeltaType

from pydantic import BaseModel

class DeltaEvent(BaseModel):
    id: UUID
    repository_name: str
    delta_type: DeltaType

    totalInsertions: int
    totalDeletions: int

    insertions: List[str]
    deletions: List[str]

    versioning_duration_ms: int
    timestamp: datetime