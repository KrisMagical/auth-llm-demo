from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth import get_password_hash
from app.database import SessionLocal
from app.main import app
from app.models import User
from app.seed import create_admin_user


def unique_email(prefix: str = "phase5") -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


def login(client: TestClient, email: str, password: str):
    return client.post("/api/login", json={"email": email, "password": password})


def test_admin_seed_creates_admin_account() -> None:
    with TestClient(app):
        db = SessionLocal()
        try:
            admin = db.query(User).filter(User.email == "admin@example.com").one()
            assert admin.role == "admin"
            assert admin.username == "admin"
            assert admin.llm_status == "seed"
            assert admin.llm_reason == "Initial admin test account for Resource B"
        finally:
            db.close()


def test_admin_test_account_can_login() -> None:
    with TestClient(app) as client:
        response = login(client, "admin@example.com", "Admin123456")

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_admin_test_account_can_access_resource_b() -> None:
    with TestClient(app) as client:
        login_response = login(client, "admin@example.com", "Admin123456")
        token = login_response.json()["access_token"]
        response = client.get(
            "/api/resource-b",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["resource"] == "B"


def test_register_ignores_extra_admin_role() -> None:
    email = unique_email("role-ignore")
    payload = {
        "username": "role_ignore",
        "email": email,
        "password": "User123456",
        "role": "admin",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)
        token = login(client, email, "User123456").json()["access_token"]
        me_response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "user"
    assert me_response.status_code == 200
    assert me_response.json()["role"] == "user"


def test_normal_user_still_cannot_access_resource_b_after_role_in_payload() -> None:
    email = unique_email("role-forbidden")
    payload = {
        "username": "role_forbidden",
        "email": email,
        "password": "User123456",
        "role": "admin",
    }

    with TestClient(app) as client:
        register_response = client.post("/api/register", json=payload)
        token = login(client, email, "User123456").json()["access_token"]
        response = client.get(
            "/api/resource-b",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert register_response.status_code == 200
    assert response.status_code == 403


def test_register_with_admin_email_returns_400() -> None:
    payload = {
        "username": "fake_admin",
        "email": "admin@example.com",
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_admin_responses_do_not_return_hashed_password() -> None:
    with TestClient(app) as client:
        token = login(client, "admin@example.com", "Admin123456").json()["access_token"]
        me_response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
        resource_response = client.get(
            "/api/resource-b",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert me_response.status_code == 200
    assert resource_response.status_code == 200
    assert "hashed_password" not in me_response.text
    assert "hashed_password" not in resource_response.text


def test_demo_accounts_endpoint_is_non_sensitive() -> None:
    with TestClient(app) as client:
        response = client.get("/api/demo-accounts")

    body = response.json()
    assert response.status_code == 200
    assert body["resource_b_test_account"]["email"] == "admin@example.com"
    assert "password_hint" in body["resource_b_test_account"]
    assert "ADMIN_PASSWORD" in body["resource_b_test_account"]["password_hint"]
    assert "password" not in body["resource_b_test_account"]


def test_create_admin_user_does_not_duplicate_existing_admin() -> None:
    with TestClient(app):
        db = SessionLocal()
        try:
            before_count = db.query(User).filter(User.email == "admin@example.com").count()
            create_admin_user(db)
            after_count = db.query(User).filter(User.email == "admin@example.com").count()
        finally:
            db.close()

    assert before_count == 1
    assert after_count == 1


def test_create_admin_user_repairs_existing_non_admin_role() -> None:
    email = unique_email("repair-admin")
    db = SessionLocal()
    try:
        user = User(
            username="repair_admin",
            email=email,
            hashed_password=get_password_hash("User123456"),
            role="user",
            llm_status="test",
            llm_reason="phase 5 role repair test",
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    import os

    previous_email = os.environ.get("ADMIN_EMAIL")
    os.environ["ADMIN_EMAIL"] = email
    try:
        db = SessionLocal()
        try:
            create_admin_user(db)
            repaired = db.query(User).filter(User.email == email).one()
            assert repaired.role == "admin"
        finally:
            db.close()
    finally:
        if previous_email is None:
            os.environ.pop("ADMIN_EMAIL", None)
        else:
            os.environ["ADMIN_EMAIL"] = previous_email
