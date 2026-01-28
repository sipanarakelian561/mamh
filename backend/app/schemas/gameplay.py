from pydantic import BaseModel

class ProblemRequest(BaseModel):
    grade: int = 1
    difficulty: int = 1  # 1 easy, 2 med, 3 hard
    count: int = 1

class ProblemOut(BaseModel):
    problem_id: str
    prompt: str
    answer: int

class SubmitAnswerRequest(BaseModel):
    problem_id: str
    answer: int
