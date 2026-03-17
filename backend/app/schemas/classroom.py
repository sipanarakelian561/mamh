from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Subject = Literal["math", "science", "reading", "writing"]


class ClassroomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    grade: int = Field(ge=1, le=12)
    subject: Subject


class ClassroomJoinRequest(BaseModel):
    class_code: str = Field(min_length=4, max_length=12)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=255)


class ClassroomOut(BaseModel):
    id: int
    name: str
    grade: int
    subject: Subject
    join_code: str
    created_at: datetime
