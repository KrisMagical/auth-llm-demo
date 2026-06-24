from fastapi.testclient import TestClient

from app.main import app


def test_home_page_returns_html() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Auth LLM Demo" in response.text


def test_register_page_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/register")

    assert response.status_code == 200


def test_login_page_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/login")

    assert response.status_code == 200


def test_me_page_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/me")

    assert response.status_code == 200


def test_resource_a_page_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/resource-a")

    assert response.status_code == 200


def test_resource_b_page_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/resource-b")

    assert response.status_code == 200


def test_demo_accounts_page_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/demo-accounts")

    assert response.status_code == 200


def test_debug_username_page_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/debug-username")

    assert response.status_code == 200


def test_register_page_contains_register_fetch() -> None:
    with TestClient(app) as client:
        response = client.get("/register")

    assert "/api/register" in response.text
    assert "fetch" in response.text


def test_pages_contain_localstorage_or_bearer_usage() -> None:
    with TestClient(app) as client:
        login_page = client.get("/login")
        resource_page = client.get("/resource-a")

    assert "localStorage" in login_page.text
    assert "Authorization" in resource_page.text
    assert "Bearer " in resource_page.text


def test_docs_still_accessible() -> None:
    with TestClient(app) as client:
        response = client.get("/docs")

    assert response.status_code == 200


def test_health_still_returns_json() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
