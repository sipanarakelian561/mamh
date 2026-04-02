import random
import uuid


def generate_addition(difficulty: int) -> tuple[str, int]:
    if difficulty == 1:
        a, b = random.randint(0, 10), random.randint(0, 10)
    elif difficulty == 2:
        a, b = random.randint(5, 50), random.randint(5, 50)
    else:
        a, b = random.randint(20, 200), random.randint(20, 200)
    prompt = f"{a} + {b} = ?"
    return prompt, a + b


def generate_problem(grade: int, difficulty: int) -> dict:
    prompt, answer = generate_addition(difficulty)
    return {
        "problem_id": str(uuid.uuid4()),
        "prompt": prompt,
        "answer": answer,
    }


def check_answer(correct_answer: int, submitted_answer: int) -> bool:
    return int(submitted_answer) == int(correct_answer)
