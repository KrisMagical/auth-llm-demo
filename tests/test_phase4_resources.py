from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def unique_email(prefix: str = "resource") -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


def register_and_login_user(client: TestClient) -> str:
    email = unique_email()
    password = "User123456"
    register_response = client.post(
        "/api/register",
        json={
            "username": "resource_user",
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def login_admin(client: TestClient) -> str:
    response = client.post(
        "/api/login",
        json={"email": "admin@example.com", "password": "Admin123456"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_resource_a_without_token_returns_401() -> None:
    with TestClient(app) as client:
        response = client.get("/api/resource-a")

    assert response.status_code == 401


def test_resource_b_without_token_returns_401() -> None:
    with TestClient(app) as client:
        response = client.get("/api/resource-b")

    assert response.status_code == 401


def test_normal_user_can_access_resource_a() -> None:
    with TestClient(app) as client:
        token = register_and_login_user(client)
        response = client.get(
            "/api/resource-a",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200


def test_normal_user_resource_a_returns_resource_a() -> None:
    with TestClient(app) as client:
        token = register_and_login_user(client)
        response = client.get(
            "/api/resource-a",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["resource"] == "A"


def test_normal_user_resource_b_returns_403() -> None:
    with TestClient(app) as client:
        token = register_and_login_user(client)
        response = client.get(
            "/api/resource-b",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403


def test_normal_user_resource_b_returns_forbidden_detail() -> None:
    with TestClient(app) as client:
        token = register_and_login_user(client)
        response = client.get(
            "/api/resource-b",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.json()["detail"] == "Forbidden: Resource B requires admin permission."


def test_admin_can_access_resource_a() -> None:
    with TestClient(app) as client:
        token = login_admin(client)
        response = client.get(
            "/api/resource-a",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200


def test_admin_can_access_resource_b() -> None:
    with TestClient(app) as client:
        token = login_admin(client)
        response = client.get(
            "/api/resource-b",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200


def test_admin_resource_b_returns_resource_b() -> None:
    with TestClient(app) as client:
        token = login_admin(client)
        response = client.get(
            "/api/resource-b",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["resource"] == "B"


def test_resource_responses_do_not_include_hashed_password() -> None:
    with TestClient(app) as client:
        user_token = register_and_login_user(client)
        admin_token = login_admin(client)
        resource_a = client.get(
            "/api/resource-a",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        resource_b = client.get(
            "/api/resource-b",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert resource_a.status_code == 200
    assert resource_b.status_code == 200
    assert "hashed_password" not in resource_a.text
    assert "hashed_password" not in resource_b.text


def test_resource_a_with_invalid_token_returns_401() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/resource-a",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401


def test_resource_b_with_invalid_token_returns_401() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/resource-b",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
