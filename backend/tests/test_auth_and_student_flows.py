from app.core.security import create_access_token
from app.models.user import User


def _register_user(client, email: str, password: str, role: str) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": role},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _login_user(client, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_register_and_login_normalizes_email(client):
    created = _register_user(client, "Student@aschool.org", "password123", "student")
    assert created["email"] == "student@aschool.org"

    token = _login_user(client, "STUDENT@ASCHOOL.ORG", "password123")
    assert isinstance(token, str)
    assert token


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "hello", "role": "student"},
    )
    assert response.status_code == 422


def test_student_progress_requires_auth(client):
    response = client.get("/api/v1/student/progress")
    assert response.status_code == 401


def test_student_progress_returns_default_values(client):
    _register_user(client, "learner@example.com", "password123", "student")
    token = _login_user(client, "learner@example.com", "password123")

    response = client.get(
        "/api/v1/student/progress",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total_xp"] == 0
    assert body["currency_balance"] == 0
    assert body["current_level"] == 1
    assert body["xp_to_next_level"] == 100
    assert body["xp_progress_percentage"] == 0
    assert body["problems_solved"] == 0


def test_teacher_cannot_access_student_progress(client):
    _register_user(client, "teacher@example.com", "password123", "teacher")
    token = _login_user(client, "teacher@example.com", "password123")

    response = client.get(
        "/api/v1/student/progress",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_inventory_equip_unequips_other_item_in_same_slot(client):
    _register_user(client, "inventory@example.com", "password123", "student")
    token = _login_user(client, "inventory@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    first_reward = client.post(
        "/api/v1/game/complete-run",
        json={"placement": 1},
        headers=headers,
    )
    assert first_reward.status_code == 200, first_reward.text

    second_reward = client.post(
        "/api/v1/game/complete-run",
        json={"placement": 1},
        headers=headers,
    )
    assert second_reward.status_code == 200, second_reward.text

    first_purchase = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "hat_1", "name": "Wizard Hat", "slot": "head", "cost": 10},
        headers=headers,
    )
    assert first_purchase.status_code == 200, first_purchase.text

    second_purchase = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "hat_2", "name": "Knight Helm", "slot": "head", "cost": 10},
        headers=headers,
    )
    assert second_purchase.status_code == 200, second_purchase.text

    equip_first = client.post(
        "/api/v1/student/inventory/equip",
        json={"item_id": "hat_1", "equipped": True},
        headers=headers,
    )
    assert equip_first.status_code == 200, equip_first.text

    equip_second = client.post(
        "/api/v1/student/inventory/equip",
        json={"item_id": "hat_2", "equipped": True},
        headers=headers,
    )
    assert equip_second.status_code == 200, equip_second.text

    inventory = client.get("/api/v1/student/inventory", headers=headers)
    assert inventory.status_code == 200, inventory.text
    by_id = {item["item_id"]: item for item in inventory.json()}
    assert by_id["hat_1"]["equipped"] is False
    assert by_id["hat_2"]["equipped"] is True


def test_rejects_token_when_claims_do_not_match_user_permissions(client, db_session):
    _register_user(client, "teststudent@example.com", "password123", "student")
    user = db_session.query(User).filter(User.email == "teststudent@example.com").first()
    assert user is not None

    forged_token = create_access_token(
        subject=str(user.id),
        role="teacher",
        is_admin=False,
    )

    response = client.get(
        "/api/v1/student/progress",
        headers={"Authorization": f"Bearer {forged_token}"},
    )
    assert response.status_code == 401


def test_teacher_progress_only_includes_their_students(client, db_session):
    _register_user(client, "teacher1@example.com", "password123", "teacher")
    _register_user(client, "teacher2@example.com", "password123", "teacher")
    _register_user(client, "student1@example.com", "password123", "student")
    _register_user(client, "student2@example.com", "password123", "student")

    teacher1 = db_session.query(User).filter(User.email == "teacher1@example.com").first()
    teacher2 = db_session.query(User).filter(User.email == "teacher2@example.com").first()
    student1 = db_session.query(User).filter(User.email == "student1@example.com").first()
    student2 = db_session.query(User).filter(User.email == "student2@example.com").first()
    assert teacher1 and teacher2 and student1 and student2

    from app.models.classroom import Classroom
    from app.models.classroom_membership import ClassroomMembership
    from app.models.progress import StudentProgress

    class1 = Classroom(
        teacher_id=teacher1.id,
        school_id=teacher1.school_id,
        name="Math 101",
        grade=5,
        subject="math",
        join_code="ABC12345",
    )
    class2 = Classroom(
        teacher_id=teacher2.id,
        school_id=teacher2.school_id,
        name="Science 101",
        grade=5,
        subject="science",
        join_code="XYZ12345",
    )
    db_session.add_all([class1, class2])
    db_session.commit()
    db_session.refresh(class1)
    db_session.refresh(class2)

    db_session.add_all(
        [
            ClassroomMembership(
                classroom_id=class1.id,
                student_id=student1.id,
                first_name="S",
                last_name="One",
                email=student1.email,
            ),
            ClassroomMembership(
                classroom_id=class2.id,
                student_id=student2.id,
                first_name="S",
                last_name="Two",
                email=student2.email,
            ),
        ]
    )
    db_session.add_all(
        [
            StudentProgress(student_id=student1.id, xp=10, level=1, problems_solved=2),
            StudentProgress(student_id=student2.id, xp=20, level=2, problems_solved=4),
        ]
    )
    db_session.commit()

    token = create_access_token(
        subject=str(teacher1.id),
        role="teacher",
        is_admin=False,
        school_id=teacher1.school_id,
    )
    response = client.get(
        "/api/v1/teacher/students/progress",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["student_id"] == student1.id
    assert body[0]["total_xp"] == 0
    assert body[0]["currency_balance"] == 0
    assert body[0]["current_level"] == 1


def test_teacher_can_change_password(client):
    _register_user(client, "teachpass@example.com", "password123", "teacher")
    token = _login_user(client, "teachpass@example.com", "password123")

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "password123", "new_password": "newpassword456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text

    # Old password should no longer work
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "teachpass@example.com", "password": "password123"},
    )
    assert response.status_code == 401

    # New password should work
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "teachpass@example.com", "password": "newpassword456"},
    )
    assert response.status_code == 200


def test_student_cannot_change_password(client):
    _register_user(client, "studpass@example.com", "password123", "student")
    token = _login_user(client, "studpass@example.com", "password123")

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "password123", "new_password": "newpassword456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_complete_run_awards_xp_money_and_levels(client):
    _register_user(client, "runner@example.com", "password123", "student")
    token = _login_user(client, "runner@example.com", "password123")

    response = client.post(
        "/api/v1/game/complete-run",
        json={"placement": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["placement"] == 1
    assert body["xp_awarded"] == 15
    assert body["money_awarded"] == 20
    assert body["total_xp"] == 15
    assert body["currency_balance"] == 20
    assert body["current_level"] == 1
    assert body["level_up"] is False


def test_student_can_purchase_item_with_currency(client):
    _register_user(client, "shopper@example.com", "password123", "student")
    token = _login_user(client, "shopper@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    reward = client.post("/api/v1/game/complete-run", json={"placement": 1}, headers=headers)
    assert reward.status_code == 200, reward.text
    assert reward.json()["currency_balance"] == 20

    purchase = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "hat_3", "name": "Shop Hat", "slot": "head", "cost": 15},
        headers=headers,
    )
    assert purchase.status_code == 200, purchase.text
    assert purchase.json()["currency_balance"] == 5

    progress = client.get("/api/v1/student/progress", headers=headers)
    assert progress.status_code == 200, progress.text
    assert progress.json()["currency_balance"] == 5


def test_quiz_completion_awards_xp_once(client, db_session):
    _register_user(client, "quizteacher@example.com", "password123", "teacher")
    _register_user(client, "quizstudent@example.com", "password123", "student")

    teacher = db_session.query(User).filter(User.email == "quizteacher@example.com").first()
    student = db_session.query(User).filter(User.email == "quizstudent@example.com").first()
    assert teacher and student

    from app.models.classroom import Classroom
    from app.models.classroom_membership import ClassroomMembership
    from app.models.quiz import Quiz, QuizQuestion

    classroom = Classroom(
        teacher_id=teacher.id,
        school_id=teacher.school_id,
        name="Quiz XP",
        grade=4,
        subject="math",
        join_code="QUIZ1234",
    )
    db_session.add(classroom)
    db_session.commit()
    db_session.refresh(classroom)

    db_session.add(
        ClassroomMembership(
            classroom_id=classroom.id,
            student_id=student.id,
            first_name="Quiz",
            last_name="Student",
            email=student.email,
        )
    )
    db_session.commit()

    quiz = Quiz(
        teacher_id=teacher.id,
        classroom_id=classroom.id,
        grade=4,
        subject="math",
        title="XP Quiz",
    )
    db_session.add(quiz)
    db_session.commit()
    db_session.refresh(quiz)

    question = QuizQuestion(
        quiz_id=quiz.id,
        order_index=0,
        prompt="2 + 2",
        answer="4",
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)

    token = create_access_token(
        subject=str(student.id),
        role="student",
        is_admin=False,
        school_id=student.school_id,
    )
    headers = {"Authorization": f"Bearer {token}"}

    first = client.post(
        f"/api/v1/student/quizzes/{quiz.id}/submit",
        json={"answers": [{"question_id": question.id, "answer": "4"}]},
        headers=headers,
    )
    assert first.status_code == 200, first.text
    assert first.json()["xp_awarded"] == 15
    assert first.json()["total_xp"] == 15

    second = client.post(
        f"/api/v1/student/quizzes/{quiz.id}/submit",
        json={"answers": [{"question_id": question.id, "answer": "4"}]},
        headers=headers,
    )
    assert second.status_code == 200, second.text
    assert second.json()["xp_awarded"] == 0
    assert second.json()["total_xp"] == 15
