from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth import create_access_token, decode_access_token
from app.database import SessionLocal
from app.main import app
from app.models import User


def unique_email(prefix: str = "auth") -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


def register_user(client: TestClient, email: str | None = None) -> dict:
    payload = {
        "username": "auth_user",
        "email": email or unique_email(),
        "password": "User123456",
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 200
    return payload


def login_user(client: TestClient, email: str, password: str = "User123456"):
    return client.post(
        "/api/login",
        json={"email": email, "password": password},
    )


def test_registered_user_can_login_successfully() -> None:
    with TestClient(app) as client:
        payload = register_user(client)
        response = login_user(client, payload["email"])

    assert response.status_code == 200


def test_login_returns_access_token_and_bearer_type() -> None:
    with TestClient(app) as client:
        payload = register_user(client)
        response = login_user(client, payload["email"])

    body = response.json()
    assert response.status_code == 200
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_with_unknown_email_returns_401() -> None:
    with TestClient(app) as client:
        response = login_user(client, unique_email("missing"))

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_with_wrong_password_returns_401() -> None:
    with TestClient(app) as client:
        payload = register_user(client)
        response = login_user(client, payload["email"], password="Wrong123456")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_response_does_not_return_hashed_password() -> None:
    with TestClient(app) as client:
        payload = register_user(client)
        response = login_user(client, payload["email"])

    assert response.status_code == 200
    assert "hashed_password" not in response.json()


def test_me_returns_current_user_with_valid_token() -> None:
    with TestClient(app) as client:
        payload = register_user(client)
        login_response = login_user(client, payload["email"])
        token = login_response.json()["access_token"]
        me_response = client.get(
            "/api/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    body = me_response.json()
    assert me_response.status_code == 200
    assert body["email"] == payload["email"]
    assert body["role"] == "user"


def test_me_response_does_not_return_hashed_password() -> None:
    with TestClient(app) as client:
        payload = register_user(client)
        token = login_user(client, payload["email"]).json()["access_token"]
        response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert "hashed_password" not in response.json()


def test_me_without_token_returns_401() -> None:
    with TestClient(app) as client:
        response = client.get("/api/me")

    assert response.status_code == 401


def test_me_with_invalid_token_returns_401() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401


def test_admin_account_can_login_successfully() -> None:
    with TestClient(app) as client:
        response = login_user(client, "admin@example.com", password="Admin123456")

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_token_payload_sub_contains_user_id() -> None:
    with TestClient(app) as client:
        payload = register_user(client)
        token = login_user(client, payload["email"]).json()["access_token"]
        decoded = decode_access_token(token)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == payload["email"]).one()
        assert decoded["sub"] == str(user.id)
    finally:
        db.close()


def test_me_with_expired_token_returns_401() -> None:
    with TestClient(app) as client:
        payload = register_user(client)
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == payload["email"]).one()
            expired_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role},
                expires_delta=timedelta(seconds=-1),
            )
        finally:
            db.close()

        response = client.get(
            "/api/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

    assert response.status_code == 401
