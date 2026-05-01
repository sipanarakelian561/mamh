from app.core.security import create_access_token
from app.models.questions import GameplayQuestion
from app.models.school import School
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
    assert body["xp_to_next_level"] == 15
    assert body["xp_progress_percentage"] == 0
    assert body["problems_solved"] == 0
    assert body["starter_monster"] is None
    assert body["equipped_monster"] is None
    assert body["starter_selected"] is False
    assert body["grade_level"] is None


def test_student_can_select_starter_once(client):
    _register_user(client, "starter@example.com", "password123", "student")
    token = _login_user(client, "starter@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    state_before = client.get("/api/v1/student/character", headers=headers)
    assert state_before.status_code == 200, state_before.text
    assert state_before.json()["starter_selected"] is False

    selected = client.post(
        "/api/v1/student/character/select",
        json={"monster": "dog"},
        headers=headers,
    )
    assert selected.status_code == 200, selected.text
    selected_body = selected.json()
    assert selected_body["starter_monster"] == "dog"
    assert selected_body["equipped_monster"] == "dog"
    assert selected_body["starter_selected"] is True

    progress = client.get("/api/v1/student/progress", headers=headers)
    assert progress.status_code == 200, progress.text
    progress_body = progress.json()
    assert progress_body["starter_monster"] == "dog"
    assert progress_body["equipped_monster"] == "dog"
    assert progress_body["starter_selected"] is True

    second_pick = client.post(
        "/api/v1/student/character/select",
        json={"monster": "dinosaur"},
        headers=headers,
    )
    assert second_pick.status_code == 409


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
        json={"item_id": "hat_1"},
        headers=headers,
    )
    assert first_purchase.status_code == 200, first_purchase.text

    second_purchase = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "hat_2"},
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
    assert body["current_level"] == 2
    assert body["xp_to_next_level"] == 25
    assert body["level_up"] is True


def test_student_can_purchase_item_with_currency(client):
    _register_user(client, "shopper@example.com", "password123", "student")
    token = _login_user(client, "shopper@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    reward = client.post("/api/v1/game/complete-run", json={"placement": 1}, headers=headers)
    assert reward.status_code == 200, reward.text
    assert reward.json()["currency_balance"] == 20

    purchase = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "hat_3"},
        headers=headers,
    )
    assert purchase.status_code == 200, purchase.text
    assert purchase.json()["currency_balance"] == 5

    progress = client.get("/api/v1/student/progress", headers=headers)
    assert progress.status_code == 200, progress.text
    assert progress.json()["currency_balance"] == 5


def test_student_shop_catalog_marks_owned_items(client):
    _register_user(client, "catalog@example.com", "password123", "student")
    token = _login_user(client, "catalog@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    reward = client.post("/api/v1/game/complete-run", json={"placement": 1}, headers=headers)
    assert reward.status_code == 200, reward.text

    purchase = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "hat_1"},
        headers=headers,
    )
    assert purchase.status_code == 200, purchase.text

    catalog = client.get("/api/v1/student/shop/items", headers=headers)
    assert catalog.status_code == 200, catalog.text
    by_id = {item["item_id"]: item for item in catalog.json()}
    assert by_id["hat_1"]["owned"] is True
    assert by_id["hat_1"]["cost"] == 10
    assert by_id["hat_2"]["owned"] is False


def test_student_purchase_rejects_duplicate_and_invalid_items(client):
    _register_user(client, "shopguard@example.com", "password123", "student")
    token = _login_user(client, "shopguard@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    reward = client.post("/api/v1/game/complete-run", json={"placement": 1}, headers=headers)
    assert reward.status_code == 200, reward.text

    first_purchase = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "hat_1"},
        headers=headers,
    )
    assert first_purchase.status_code == 200, first_purchase.text

    duplicate = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "hat_1"},
        headers=headers,
    )
    assert duplicate.status_code == 409, duplicate.text

    invalid = client.post(
        "/api/v1/student/inventory/purchase",
        json={"item_id": "not-a-real-item"},
        headers=headers,
    )
    assert invalid.status_code == 404, invalid.text


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
    assert first.json()["current_level"] == 2

    second = client.post(
        f"/api/v1/student/quizzes/{quiz.id}/submit",
        json={"answers": [{"question_id": question.id, "answer": "4"}]},
        headers=headers,
    )
    assert second.status_code == 200, second.text
    assert second.json()["xp_awarded"] == 0
    assert second.json()["total_xp"] == 15


def test_admin_can_create_student_with_grade_level(client, db_session):
    school = School(name="Grade School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    admin = User(
        email="super@example.com",
        password_hash="ignored",
        role="super_admin",
        is_admin=True,
        school_id=None,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    token = create_access_token(subject=str(admin.id), role="super_admin", is_admin=True)
    response = client.post(
        "/api/v1/admin/users",
        json={
            "first_name": "Grade",
            "last_name": "Student",
            "role": "student",
            "password": "password123",
            "school_id": school.id,
            "grade_level": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["grade_level"] == 1


def test_gameplay_blocks_students_without_assigned_grade(client):
    _register_user(client, "nograde@example.com", "password123", "student")
    token = _login_user(client, "nograde@example.com", "password123")

    response = client.post(
        "/api/v1/game/questions",
        json={"subject": "math", "count": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "Student grade not assigned"


def test_gameplay_returns_questions_for_student_grade_and_subject(client, db_session):
    _register_user(client, "gradeplay@example.com", "password123", "student")
    student = db_session.query(User).filter(User.email == "gradeplay@example.com").first()
    assert student is not None
    student.grade_level = 1
    db_session.add(student)

    db_session.add_all(
        [
            GameplayQuestion(
                grade=1,
                subject="math",
                difficulty="easy",
                prompt="What is 2 + 2?",
                answer_a="1",
                answer_b="4",
                answer_c="5",
                answer_d="12",
                correct_index=1,
                active=True,
            ),
            GameplayQuestion(
                grade=2,
                subject="math",
                difficulty="easy",
                prompt="What is 9 + 1?",
                answer_a="8",
                answer_b="9",
                answer_c="10",
                answer_d="11",
                correct_index=2,
                active=True,
            ),
            GameplayQuestion(
                grade=1,
                subject="english",
                difficulty="easy",
                prompt="Which word is a noun?",
                answer_a="run",
                answer_b="happy",
                answer_c="cat",
                answer_d="quickly",
                correct_index=2,
                active=True,
            ),
        ]
    )
    db_session.commit()

    token = _login_user(client, "gradeplay@example.com", "password123")
    response = client.post(
        "/api/v1/game/questions",
        json={"subject": "math", "count": 3},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["grade_level"] == 1
    assert body["subject"] == "math"
    assert len(body["questions"]) == 1
    assert body["questions"][0]["prompt"] == "What is 2 + 2?"
    assert "correct_index" not in body["questions"][0]


def test_gameplay_submit_checks_db_question_for_student_grade(client, db_session):
    _register_user(client, "gradeanswer@example.com", "password123", "student")
    student = db_session.query(User).filter(User.email == "gradeanswer@example.com").first()
    assert student is not None
    student.grade_level = 1
    db_session.add(student)

    question = GameplayQuestion(
        grade=1,
        subject="math",
        difficulty="easy",
        prompt="What is 3 + 1?",
        answer_a="3",
        answer_b="4",
        answer_c="5",
        answer_d="6",
        correct_index=1,
        active=True,
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)

    token = _login_user(client, "gradeanswer@example.com", "password123")
    response = client.post(
        "/api/v1/game/submit",
        json={"question_id": question.id, "selected_index": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["correct"] is True
