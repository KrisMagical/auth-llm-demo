from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_exists() -> None:
    assert (PROJECT_ROOT / "README.md").exists()


def test_readme_contains_project_title() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Auth LLM Demo" in content


def test_readme_contains_register_api() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "/api/register" in content


def test_readme_contains_login_api() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "/api/login" in content


def test_readme_contains_resource_a_api() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "/api/resource-a" in content


def test_readme_contains_resource_b_api() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "/api/resource-b" in content


def test_readme_contains_openai_api_key() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "OPENAI_API_KEY" in content


def test_readme_contains_admin_email() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "admin@example.com" in content


def test_readme_contains_admin_password() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Admin123456" in content


def test_readme_contains_mock_checker_or_fallback() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "mock checker" in content or "mock fallback" in content


def test_readme_contains_localstorage() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "localStorage" in content


def test_readme_contains_curl_examples() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "curl -X POST" in content


def test_readme_contains_env_security_note() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "不要提交 `.env`" in content or "`.env` 不应提交到 GitHub" in content


def test_report_exists() -> None:
    assert (PROJECT_ROOT / "REPORT.md").exists()


def test_docs_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/docs")

    assert response.status_code == 200


def test_openapi_json_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200


def test_openapi_json_contains_core_api_routes() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    paths = response.json()["paths"]
    assert "/api/register" in paths
    assert "/api/login" in paths
    assert "/api/resource-a" in paths
    assert "/api/resource-b" in paths
