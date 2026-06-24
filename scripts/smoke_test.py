"""Smoke test for local or public auth-llm-demo deployments."""

import json
import os
import sys
import time
import urllib.error
import urllib.request


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


class SmokeTestError(Exception):
    """Raised when a smoke test step fails."""


def request_json(
    method: str,
    path: str,
    data: dict | None = None,
    token: str | None = None,
    expected_status: int = 200,
) -> dict:
    url = f"{BASE_URL}{path}"
    body = None
    headers = {}
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status_code = response.status
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status_code = exc.code
        response_body = exc.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise SmokeTestError(f"{method} {path} failed: {exc}") from exc

    if status_code != expected_status:
        raise SmokeTestError(
            f"{method} {path} expected {expected_status}, got {status_code}: {response_body}"
        )

    if not response_body:
        return {}
    try:
        return json.loads(response_body)
    except json.JSONDecodeError:
        return {"raw": response_body}


def pass_step(message: str) -> None:
    print(f"PASS {message}")


def run() -> None:
    timestamp = int(time.time())
    user_email = f"smoke_{timestamp}@example.com"
    user_password = "User123456"

    health = request_json("GET", "/health")
    if health != {"status": "ok"}:
        raise SmokeTestError(f"Unexpected health response: {health}")
    pass_step("GET /health")

    register_response = request_json(
        "POST",
        "/api/register",
        {
            "username": f"smoke_user_{timestamp}",
            "email": user_email,
            "password": user_password,
        },
    )
    if register_response.get("user", {}).get("email") != user_email:
        raise SmokeTestError(f"Unexpected register response: {register_response}")
    pass_step("POST /api/register")

    login_response = request_json(
        "POST",
        "/api/login",
        {"email": user_email, "password": user_password},
    )
    user_token = login_response.get("access_token")
    if not user_token:
        raise SmokeTestError("User login did not return access token")
    pass_step("POST /api/login user token acquired")

    resource_a = request_json("GET", "/api/resource-a", token=user_token)
    if resource_a.get("resource") != "A":
        raise SmokeTestError(f"Unexpected Resource A response: {resource_a}")
    pass_step("GET /api/resource-a as user")

    request_json(
        "GET",
        "/api/resource-b",
        token=user_token,
        expected_status=403,
    )
    pass_step("GET /api/resource-b as user returned 403")

    admin_login = request_json(
        "POST",
        "/api/login",
        {"email": "admin@example.com", "password": "Admin123456"},
    )
    admin_token = admin_login.get("access_token")
    if not admin_token:
        raise SmokeTestError("Admin login did not return access token")
    pass_step("POST /api/login admin token acquired")

    resource_b = request_json("GET", "/api/resource-b", token=admin_token)
    if resource_b.get("resource") != "B":
        raise SmokeTestError(f"Unexpected Resource B response: {resource_b}")
    pass_step("GET /api/resource-b as admin")

    username_check = request_json(
        "POST",
        "/api/debug/check-username",
        {"username": "official_admin"},
    )
    status = username_check.get("status", "")
    if "rejected" not in status:
        raise SmokeTestError(f"Unexpected username check response: {username_check}")
    pass_step("POST /api/debug/check-username official_admin rejected")


def main() -> int:
    print(f"Running smoke test against {BASE_URL}")
    try:
        run()
    except SmokeTestError as exc:
        print(f"FAIL {exc}")
        return 1

    print("PASS smoke test completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
