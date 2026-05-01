from pydantic import BaseModel


class ProgressOut(BaseModel):
    student_id: int
    xp: int
    level: int
    grade_level: int | None = None
    total_xp: int
    currency_balance: int
    current_level: int
    xp_to_next_level: int
    xp_progress_percentage: float
    problems_solved: int
    starter_monster: str | None = None
    equipped_monster: str | None = None
    starter_selected: bool = False
