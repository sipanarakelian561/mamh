from pydantic import BaseModel


class ProgressOut(BaseModel):
    student_id: int
    xp: int
    level: int
    problems_solved: int
