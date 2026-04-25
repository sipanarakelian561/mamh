from pydantic import BaseModel


class ProgressOut(BaseModel):
    student_id: int
    xp: int
    level: int
    total_xp: int
    currency_balance: int
    current_level: int
    xp_to_next_level: int
    xp_progress_percentage: float
    problems_solved: int
