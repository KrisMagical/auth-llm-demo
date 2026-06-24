from fastapi.testclient import TestClient

from app.auth import get_password_hash, verify_password
from app.main import app


def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_debug_users_count_has_seeded_admin() -> None:
    with TestClient(app) as client:
        response = client.get("/debug/users/count")

    assert response.status_code == 200
    assert response.json()["count"] >= 1


def test_password_hash_and_verify() -> None:
    password = "Admin123456"
    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrong-password", hashed_password)
