from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.progress_service import (
    FIRST_PLACE_XP,
    SECOND_PLACE_XP,
    THIRD_PLACE_XP,
    add_xp,
)

FIRST_PLACE_MONEY = 20
SECOND_PLACE_MONEY = 10
THIRD_PLACE_MONEY = 5

PLACEMENT_XP_REWARDS = {
    1: FIRST_PLACE_XP,
    2: SECOND_PLACE_XP,
    3: THIRD_PLACE_XP,
}

PLACEMENT_MONEY_REWARDS = {
    1: FIRST_PLACE_MONEY,
    2: SECOND_PLACE_MONEY,
    3: THIRD_PLACE_MONEY,
}


@dataclass
class GameRewardResult:
    student_id: int
    placement: int
    xp_awarded: int
    money_awarded: int
    total_xp: int
    current_level: int
    xp_to_next_level: int
    xp_progress_percentage: float
    currency_balance: int
    level_up: bool
    problems_solved: int


def award_game_placement(db: Session, student_id: int, placement: int) -> GameRewardResult:
    if placement not in PLACEMENT_XP_REWARDS:
        raise ValueError("Placement must be 1, 2, or 3")

    update = add_xp(
        db,
        student_id,
        PLACEMENT_XP_REWARDS[placement],
        money_amount=PLACEMENT_MONEY_REWARDS[placement],
    )
    return GameRewardResult(
        student_id=update.student_id,
        placement=placement,
        xp_awarded=PLACEMENT_XP_REWARDS[placement],
        money_awarded=PLACEMENT_MONEY_REWARDS[placement],
        total_xp=update.total_xp,
        current_level=update.current_level,
        xp_to_next_level=update.xp_to_next_level,
        xp_progress_percentage=update.xp_progress_percentage,
        currency_balance=update.currency_balance,
        level_up=update.level_up,
        problems_solved=update.problems_solved,
    )


def get_student_balance_or_404(db: Session, student_id: int) -> User:
    user = db.get(User, student_id)
    if not user or user.role != "student":
        raise ValueError("Student not found")
    return user


def spend_money(db: Session, student_id: int, amount: int) -> User:
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")

    student = get_student_balance_or_404(db, student_id)
    if student.currency_balance < amount:
        raise ValueError("Insufficient funds")

    student.currency_balance -= amount
    db.add(student)
    db.commit()
    db.refresh(student)
    return student
