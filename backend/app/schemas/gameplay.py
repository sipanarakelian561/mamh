from typing import Literal

from pydantic import BaseModel, Field

Subject = Literal["math", "english"]


class ProblemRequest(BaseModel):
    subject: Subject
    count: int = Field(ge=1, le=20)
    exclude_question_ids: list[int] = Field(default_factory=list, max_length=200)


class SubmitAnswerRequest(BaseModel):
    question_id: int = Field(ge=1)
    selected_index: int = Field(ge=0, le=3)


class GameResultRequest(BaseModel):
    placement: int = Field(ge=1, le=3)


class GameResultResponse(BaseModel):
    student_id: int
    placement: int
    xp_awarded: int
    money_awarded: int
    total_xp: int
    currency_balance: int
    current_level: int
    xp_to_next_level: int
    xp_progress_percentage: float
    level_up: bool
    problems_solved: int
