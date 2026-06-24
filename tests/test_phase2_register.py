from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth import verify_password
from app.database import SessionLocal
from app.main import app
from app.models import User


def unique_email(prefix: str = "user") -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


def test_register_user_success() -> None:
    payload = {
        "username": "normal_user",
        "email": unique_email(),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "registered successfully"
    assert body["user"]["username"] == payload["username"]
    assert body["user"]["email"] == payload["email"]


def test_registered_user_defaults_to_user_role() -> None:
    payload = {
        "username": "role_user",
        "email": unique_email("role"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "user"


def test_register_response_does_not_return_hashed_password() -> None:
    payload = {
        "username": "safe_user",
        "email": unique_email("safe"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert "hashed_password" not in response.json()["user"]


def test_registered_user_has_mock_llm_status() -> None:
    payload = {
        "username": "llm_later",
        "email": unique_email("llm"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    user = response.json()["user"]
    assert response.status_code == 200
    assert user["llm_status"] == "mock_allowed"
    assert user["llm_reason"] == "Mock checker passed."


def test_duplicate_email_returns_400() -> None:
    email = unique_email("duplicate")
    first_payload = {
        "username": "first_user",
        "email": email,
        "password": "User123456",
    }
    second_payload = {
        "username": "second_user",
        "email": email,
        "password": "User123456",
    }

    with TestClient(app) as client:
        first_response = client.post("/api/register", json=first_payload)
        second_response = client.post("/api/register", json=second_payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email already registered"


def test_password_is_hashed_in_database() -> None:
    password = "User123456"
    email = unique_email("hash")
    payload = {
        "username": "hash_user",
        "email": email,
        "password": password,
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).one()
        assert user.hashed_password != password
        assert verify_password(password, user.hashed_password)
    finally:
        db.close()


def test_admin_email_cannot_be_overwritten_by_register() -> None:
    payload = {
        "username": "not_admin",
        "email": "admin@example.com",
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 400

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@example.com").one()
        assert admin.username == "admin"
        assert admin.role == "admin"
    finally:
        db.close()


def test_username_too_short_fails_validation() -> None:
    payload = {
        "username": "a",
        "email": unique_email("short-name"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 422


def test_password_too_short_fails_validation() -> None:
    payload = {
        "username": "short_password",
        "email": unique_email("short-pass"),
        "password": "short",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 422
