from typing import Literal

from pydantic import BaseModel, Field

Subject = Literal["math", "english"]


class QuestionBankCreate(BaseModel):
    grade: int = Field(ge=1, le=6)
    subject: Subject
    difficulty: str = Field(default="easy", min_length=1, max_length=20)
    prompt: str = Field(min_length=1)
    answers: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    active: bool = True


class QuestionBankUpdate(BaseModel):
    grade: int | None = Field(default=None, ge=1, le=6)
    subject: Subject | None = None
    difficulty: str | None = Field(default=None, min_length=1, max_length=20)
    prompt: str | None = Field(default=None, min_length=1)
    answers: list[str] | None = Field(default=None, min_length=4, max_length=4)
    correct_index: int | None = Field(default=None, ge=0, le=3)
    active: bool | None = None


class QuestionBankOut(BaseModel):
    id: int
    teacher_id: int | None
    grade: int
    subject: Subject
    difficulty: str
    prompt: str
    answers: list[str]
    correct_index: int
    active: bool
