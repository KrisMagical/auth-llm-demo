from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_file(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_readme_contains_render() -> None:
    assert "Render" in read_file("README.md")


def test_readme_contains_railway() -> None:
    assert "Railway" in read_file("README.md")


def test_readme_contains_base_url() -> None:
    assert "BASE_URL" in read_file("README.md")


def test_readme_contains_public_deployment_checklist() -> None:
    assert "公网部署验收清单" in read_file("README.md")


def test_readme_contains_jwt_secret() -> None:
    assert "JWT_SECRET" in read_file("README.md")


def test_readme_contains_admin_password() -> None:
    assert "ADMIN_PASSWORD" in read_file("README.md")


def test_readme_contains_openai_api_key() -> None:
    assert "OPENAI_API_KEY" in read_file("README.md")


def test_readme_contains_docker_build() -> None:
    assert "docker build" in read_file("README.md")


def test_readme_contains_docker_run() -> None:
    assert "docker run" in read_file("README.md")


def test_readme_contains_health() -> None:
    assert "/health" in read_file("README.md")


def test_readme_contains_docs() -> None:
    assert "/docs" in read_file("README.md")


def test_readme_contains_resource_a_api() -> None:
    assert "/api/resource-a" in read_file("README.md")


def test_readme_contains_resource_b_api() -> None:
    assert "/api/resource-b" in read_file("README.md")


def test_report_contains_public_url_section() -> None:
    assert "公网访问地址" in read_file("REPORT.md")


def test_report_does_not_contain_example_dot_com_final_url() -> None:
    assert "https://example.com" not in read_file("REPORT.md")


def test_deployment_doc_exists() -> None:
    assert (PROJECT_ROOT / "docs" / "deployment.md").exists()


def test_deployment_doc_contains_render_railway_and_env() -> None:
    content = read_file("docs/deployment.md")
    assert "Render" in content
    assert "Railway" in content
    assert "环境变量" in content
