from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

import app.llm_guard as llm_guard
from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def unique_email(prefix: str = "deepseek") -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


def fake_openai_class(content: str | None = None, error: Exception | None = None):
    class FakeCompletions:
        def create(self, **kwargs):
            if error:
                raise error
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=content),
                    )
                ]
            )

    class FakeOpenAI:
        def __init__(self, api_key: str, base_url: str | None = None):
            self.api_key = api_key
            self.base_url = base_url
            self.chat = SimpleNamespace(completions=FakeCompletions())

    return FakeOpenAI


def test_deepseek_without_api_key_normal_user_returns_mock_allowed(
    monkeypatch,
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = llm_guard.check_username("normal_user")

    assert result["provider"] == "mock"
    assert result["status"] == "mock_allowed"


def test_deepseek_without_api_key_official_admin_returns_mock_rejected(
    monkeypatch,
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    result = llm_guard.check_username("official_admin")

    assert result["provider"] == "mock"
    assert result["status"] == "mock_rejected"


def test_deepseek_allowed_json_returns_allowed(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setattr(
        llm_guard,
        "OpenAI",
        fake_openai_class('{"status":"allowed","reason":"Looks fine."}'),
    )

    result = llm_guard.check_username("normal_user")

    assert result["provider"] == "deepseek"
    assert result["status"] == "allowed"
    assert result["reason"] == "Looks fine."


def test_deepseek_rejected_json_returns_rejected(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setattr(
        llm_guard,
        "OpenAI",
        fake_openai_class('{"status":"rejected","reason":"Risky username."}'),
    )

    result = llm_guard.check_username("official_admin")

    assert result["provider"] == "deepseek"
    assert result["status"] == "rejected"
    assert result["reason"] == "Risky username."


def test_deepseek_uncertain_json_returns_uncertain(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setattr(
        llm_guard,
        "OpenAI",
        fake_openai_class('{"status":"uncertain","reason":"Borderline."}'),
    )

    result = llm_guard.check_username("borderline_user")

    assert result["provider"] == "deepseek"
    assert result["status"] == "uncertain"
    assert result["reason"] == "Borderline."


def test_deepseek_invalid_json_returns_failed(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setattr(llm_guard, "OpenAI", fake_openai_class("not json"))

    result = llm_guard.check_username("normal_user")

    assert result["provider"] == "deepseek"
    assert result["status"] == "failed"
    assert result["reason"] == "LLM returned invalid JSON."


def test_deepseek_exception_returns_failed(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setattr(
        llm_guard,
        "OpenAI",
        fake_openai_class(error=RuntimeError("network unavailable")),
    )

    result = llm_guard.check_username("normal_user")

    assert result["provider"] == "deepseek"
    assert result["status"] == "failed"
    assert result["reason"].startswith("DeepSeek check failed:")


def test_register_with_deepseek_allowed_succeeds(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.check_username",
        lambda username: {
            "status": "allowed",
            "reason": "DeepSeek checker passed.",
            "provider": "deepseek",
        },
    )
    payload = {
        "username": "deepseek_allowed_user",
        "email": unique_email("allowed"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 200
    assert response.json()["user"]["llm_status"] == "allowed"
    assert response.json()["user"]["llm_reason"] == "DeepSeek checker passed."


def test_register_with_deepseek_rejected_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.check_username",
        lambda username: {
            "status": "rejected",
            "reason": "DeepSeek rejected username.",
            "provider": "deepseek",
        },
    )
    payload = {
        "username": "deepseek_rejected_user",
        "email": unique_email("rejected"),
        "password": "User123456",
    }

    with TestClient(app) as client:
        response = client.post("/api/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Username rejected: DeepSeek rejected username."
    )


def test_readme_contains_deepseek_configuration() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "DEEPSEEK_API_KEY" in readme
    assert "LLM_PROVIDER=deepseek" in readme


def test_env_example_contains_deepseek_model() -> None:
    env_example = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")

    assert "DEEPSEEK_MODEL=deepseek-chat" in env_example


def test_docker_files_do_not_contain_deepseek_api_key_value() -> None:
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    compose = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "DEEPSEEK_API_KEY" not in dockerfile
    assert "your-deepseek-api-key" not in dockerfile
    assert "DEEPSEEK_API_KEY" not in compose
    assert "your-deepseek-api-key" not in compose
