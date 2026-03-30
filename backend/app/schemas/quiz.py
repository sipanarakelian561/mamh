from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Subject = Literal["math", "science", "reading", "writing"]


class QuizQuestionCreate(BaseModel):
    prompt: str = Field(min_length=1)
    answer: str | None = None


class QuizCreate(BaseModel):
    classroom_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    questions: list[QuizQuestionCreate] = Field(min_length=1)


class QuizQuestionOut(BaseModel):
    id: int
    order_index: int
    prompt: str
    answer: str | None


class QuizOut(BaseModel):
    id: int
    classroom_id: int
    grade: int
    subject: Subject
    classroom_name: str
    title: str
    created_at: datetime
    questions: list[QuizQuestionOut]


class QuizSubmitAnswer(BaseModel):
    question_id: int
    answer: str


class QuizSubmitRequest(BaseModel):
    answers: list[QuizSubmitAnswer] = Field(min_length=1)
