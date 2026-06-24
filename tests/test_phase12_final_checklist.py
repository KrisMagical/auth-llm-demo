from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_file(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_final_checklist_exists() -> None:
    assert (PROJECT_ROOT / "docs" / "final_checklist.md").exists()


def test_final_checklist_contains_local_run_section() -> None:
    assert "本地运行验收" in read_file("docs/final_checklist.md")


def test_final_checklist_contains_register_login_section() -> None:
    assert "注册 / 登录验收" in read_file("docs/final_checklist.md")


def test_final_checklist_contains_resource_auth_section() -> None:
    assert "资源 A / B 授权验收" in read_file("docs/final_checklist.md")


def test_final_checklist_contains_llm_mock_section() -> None:
    assert "LLM / mock 用户名审核验收" in read_file("docs/final_checklist.md")


def test_final_checklist_contains_docker_section() -> None:
    assert "Docker 验收" in read_file("docs/final_checklist.md")


def test_final_checklist_contains_public_deployment_section() -> None:
    assert "公网部署验收" in read_file("docs/final_checklist.md")


def test_final_checklist_contains_admin_email() -> None:
    assert "admin@example.com" in read_file("docs/final_checklist.md")


def test_smoke_test_exists() -> None:
    assert (PROJECT_ROOT / "scripts" / "smoke_test.py").exists()


def test_smoke_test_contains_base_url() -> None:
    assert "BASE_URL" in read_file("scripts/smoke_test.py")


def test_smoke_test_contains_register_api() -> None:
    assert "/api/register" in read_file("scripts/smoke_test.py")


def test_smoke_test_contains_resource_a_api() -> None:
    assert "/api/resource-a" in read_file("scripts/smoke_test.py")


def test_smoke_test_contains_resource_b_api() -> None:
    assert "/api/resource-b" in read_file("scripts/smoke_test.py")


def test_smoke_test_does_not_print_full_access_token() -> None:
    content = read_file("scripts/smoke_test.py")
    assert "print(user_token" not in content
    assert "print(admin_token" not in content


def test_readme_mentions_smoke_test() -> None:
    assert "smoke_test.py" in read_file("README.md")


def test_report_mentions_final_checklist() -> None:
    assert "final_checklist" in read_file("REPORT.md")
