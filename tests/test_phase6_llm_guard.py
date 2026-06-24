from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.llm_guard import check_username, parse_llm_response
from app.main import app
from app.models import User


def unique_email(prefix: str = "phase6") -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


def test_without_openai_key_normal_user_returns_mock_allowed() -> None:
    result = check_username("normal_user")

    assert result["status"] == "mock_allowed"
    assert result["reason"] == "Mock checker passed."
    assert result["provider"] == "mock"


def test_without_openai_key_official_admin_returns_mock_rejected() -> None:
    result = check_username("official_admin")

    assert result["status"] == "mock_rejected"
    assert result["reason"] == "Mock checker detected risky keyword."
    assert result["provider"] == "mock"


def test_mock_checker_is_case_insensitive() -> None:
    result = check_username("Official_Admin")

    assert result["status"] == "mock_rejected"


def test_register_normal_user_succeeds_with_mock_allowed() -> None:
    payload = {
        "username": "normal_user",
        "email": unique_email("mock-allowed"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert response.json()["user"]["llm_status"] == "mock_allowed"


def test_register_official_admin_fails_with_400() -> None:
    payload = {
        "username": "official_admin",
        "email": unique_email("mock-rejected"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"].startswith("Username rejected:")


def test_rejected_register_does_not_create_user() -> None:
    email = unique_email("not-created")
    payload = {
        "username": "official_admin",
        "email": email,
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 400

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is None
    finally:
        db.close()


def test_uncertain_status_allows_register(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.check_username",
        lambda username: {
            "status": "uncertain",
            "reason": "Borderline username.",
            "provider": "openai",
        },
    )
    payload = {
        "username": "borderline_user",
        "email": unique_email("uncertain"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert response.json()["user"]["llm_status"] == "uncertain"


def test_failed_status_allows_register(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.check_username",
        lambda username: {
            "status": "failed",
            "reason": "LLM username check failed.",
            "provider": "openai",
        },
    )
    payload = {
        "username": "fallback_user",
        "email": unique_email("failed"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert response.json()["user"]["llm_status"] == "failed"


def test_allowed_status_allows_register(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.check_username",
        lambda username: {
            "status": "allowed",
            "reason": "LLM checker passed.",
            "provider": "openai",
        },
    )
    payload = {
        "username": "llm_allowed_user",
        "email": unique_email("allowed"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert response.json()["user"]["llm_status"] == "allowed"


def test_register_response_does_not_return_hashed_password() -> None:
    payload = {
        "username": "phase6_safe_user",
        "email": unique_email("no-hash"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert "hashed_password" not in response.json()["user"]


def test_role_injection_protection_still_applies() -> None:
    payload = {
        "username": "phase6_role_user",
        "email": unique_email("role"),
        "password": "User123456",
        "role": "admin",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "user"


def test_debug_check_username_returns_mock_result() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/debug/check-username",
            json={"username": "official_admin"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "mock_rejected"
    assert response.json()["provider"] == "mock"


def test_parse_llm_response_invalid_json_returns_failed() -> None:
    result = parse_llm_response("not json")

    assert result["status"] == "failed"
    assert result["reason"] == "LLM returned invalid JSON."
    assert result["provider"] == "openai"


def test_parse_llm_response_invalid_status_returns_failed() -> None:
    result = parse_llm_response('{"status":"blocked","reason":"bad"}')

    assert result["status"] == "failed"
    assert result["reason"] == "LLM returned invalid status."


def test_parse_llm_response_accepts_json_code_fence() -> None:
    result = parse_llm_response(
        '```json\n{"status":"allowed","reason":"Looks fine."}\n```'
    )

    assert result["status"] == "allowed"
    assert result["reason"] == "Looks fine."
