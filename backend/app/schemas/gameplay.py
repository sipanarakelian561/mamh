from pydantic import BaseModel, Field


class ProblemRequest(BaseModel):
    grade: int = Field(ge=1, le=12)
    difficulty: int = Field(ge=1, le=3)
    count: int = Field(ge=1, le=20)


class SubmitAnswerRequest(BaseModel):
    problem_id: str = Field(min_length=1)
    answer: int


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
