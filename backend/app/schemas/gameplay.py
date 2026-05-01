from pydantic import BaseModel, Field


class ProblemRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=50)
    count: int = Field(ge=1, le=20)


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
