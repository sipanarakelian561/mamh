import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.questions import GameplayQuestion

QUESTION_BANK_DIR = Path(__file__).parent / "question_bank"


def load_question_bank() -> list[dict]:
    questions: list[dict] = []
    
    for path in QUESTION_BANK_DIR.rglob("*.json"):
        with path.open("r", encoding="utf-8") as f:
            raw = f.read().strip()
            if not raw:
                continue
            data = json.loads(raw)
            if isinstance(data, list):
                questions.extend(data)
                
    return questions


def seed_gameplay_questions(db: Session) -> None:
    existing_count = db.query(GameplayQuestion).count()
    if existing_count > 0:
        return

    raw_questions = load_question_bank()

    for q in raw_questions:
        if not isinstance(q, dict):
            continue

        answers = q.get("answers")
        prompt = q.get("prompt")
        grade = q.get("grade")
        subject = q.get("subject")
        correct_index = q.get("correct_index")

        if (
            not prompt
            or grade is None
            or not subject
            or not isinstance(answers, list)
            or len(answers) != 4
            or correct_index is None
        ):
            continue

        answers = q["answers"]

        question = GameplayQuestion(
            teacher_id=None,
            grade=q["grade"],
            subject=str(q["subject"]).lower(),
            difficulty=q.get("difficulty", "easy"),
            prompt=q["prompt"],
            answer_a=answers[0],
            answer_b=answers[1],
            answer_c=answers[2],
            answer_d=answers[3],
            correct_index=q["correct_index"],
            active=q.get("active", True),
        )
        db.add(question)

    db.commit()
