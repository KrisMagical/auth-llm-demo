from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_file(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_dockerfile_exists() -> None:
    assert (PROJECT_ROOT / "Dockerfile").exists()


def test_dockerfile_uses_python_312_slim() -> None:
    assert "python:3.12-slim" in read_file("Dockerfile")


def test_dockerfile_runs_uvicorn_app() -> None:
    content = read_file("Dockerfile")
    assert "uvicorn app.main:app" in content


def test_dockerfile_does_not_contain_openai_api_key_value() -> None:
    content = read_file("Dockerfile")
    assert "your-openai-api-key" not in content


def test_dockerfile_does_not_contain_sk_secret_prefix() -> None:
    assert "sk-" not in read_file("Dockerfile")


def test_dockerignore_exists() -> None:
    assert (PROJECT_ROOT / ".dockerignore").exists()


def test_dockerignore_excludes_env() -> None:
    assert ".env" in read_file(".dockerignore")


def test_dockerignore_excludes_db_files() -> None:
    assert "*.db" in read_file(".dockerignore")


def test_dockerignore_excludes_venv() -> None:
    assert ".venv" in read_file(".dockerignore")


def test_docker_compose_exists() -> None:
    assert (PROJECT_ROOT / "docker-compose.yml").exists()


def test_docker_compose_contains_service_name() -> None:
    assert "auth-llm-demo" in read_file("docker-compose.yml")


def test_docker_compose_maps_port_8000() -> None:
    assert '"8000:8000"' in read_file("docker-compose.yml")


def test_docker_compose_uses_env_file_or_environment() -> None:
    content = read_file("docker-compose.yml")
    assert "env_file" in content or "environment" in content


def test_readme_contains_docker_build_command() -> None:
    assert "docker build -t auth-llm-demo ." in read_file("README.md")


def test_readme_contains_docker_run_command() -> None:
    assert "docker run --rm -p 8000:8000 --env-file .env auth-llm-demo" in read_file(
        "README.md"
    )


def test_readme_contains_docker_compose_command() -> None:
    assert "docker compose up --build" in read_file("README.md")


def test_report_contains_docker_progress() -> None:
    content = read_file("REPORT.md")
    assert "Dockerfile" in content or "Docker 化" in content
