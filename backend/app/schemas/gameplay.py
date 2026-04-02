from pydantic import BaseModel, Field


class ProblemRequest(BaseModel):
    grade: int = Field(ge=1, le=12)
    difficulty: int = Field(ge=1, le=3)
    count: int = Field(ge=1, le=20)


class SubmitAnswerRequest(BaseModel):
    problem_id: str = Field(min_length=1)
    answer: int
