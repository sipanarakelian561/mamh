from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Subject = Literal["math", "english"]


class QuizQuestionCreate(BaseModel):
    prompt: str = Field(min_length=1)
    answers: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)


class QuizCreate(BaseModel):
    classroom_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    questions: list[QuizQuestionCreate] = Field(min_length=1)


class QuizQuestionOut(BaseModel):
    id: int
    order_index: int
    prompt: str
    answers: list[str]
    correct_index: int


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
    selected_index: int | None = Field(default=None, ge=0, le=3)
    answer: str | None = None


class QuizSubmitRequest(BaseModel):
    answers: list[QuizSubmitAnswer] = Field(min_length=1)
