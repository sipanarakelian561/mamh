from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Subject = Literal["math", "science", "reading", "writing"]


class AssignmentCreate(BaseModel):
    classroom_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class AssignmentOut(BaseModel):
    id: int
    classroom_id: int
    grade: int
    subject: Subject
    classroom_name: str
    title: str
    content: str
    created_at: datetime
