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
    created = _register_user(client, "Student@OneSchool.org", "password123", "student")
    assert created["email"] == "student@oneschool.org"

    token = _login_user(client, "STUDENT@ONESCHOOL.ORG", "password123")
    assert isinstance(token, str)
    assert token


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "short", "role": "student"},
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
    assert body["xp"] == 0
    assert body["level"] == 1
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

    first_add = client.post(
        "/api/v1/student/inventory/add",
        json={"item_id": "hat_1", "name": "Wizard Hat", "slot": "head"},
        headers=headers,
    )
    assert first_add.status_code == 200, first_add.text

    second_add = client.post(
        "/api/v1/student/inventory/add",
        json={"item_id": "hat_2", "name": "Knight Helm", "slot": "head"},
        headers=headers,
    )
    assert second_add.status_code == 200, second_add.text

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
