from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_file(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_submission_doc_exists() -> None:
    assert (PROJECT_ROOT / "docs" / "submission.md").exists()


def test_submission_doc_contains_title() -> None:
    assert "Submission Summary" in read_file("docs/submission.md")


def test_submission_doc_contains_project_repository() -> None:
    assert "Project Repository" in read_file("docs/submission.md")


def test_submission_doc_contains_public_url() -> None:
    assert "Public URL" in read_file("docs/submission.md")


def test_submission_doc_contains_resource_b_account() -> None:
    assert "Resource B Test Account" in read_file("docs/submission.md")


def test_submission_doc_contains_admin_email() -> None:
    assert "admin@example.com" in read_file("docs/submission.md")


def test_submission_doc_contains_admin_password() -> None:
    assert "Admin123456" in read_file("docs/submission.md")


def test_submission_doc_contains_smoke_test() -> None:
    assert "smoke_test.py" in read_file("docs/submission.md")


def test_submission_doc_contains_docker() -> None:
    assert "Docker" in read_file("docs/submission.md")


def test_readme_mentions_submission_doc() -> None:
    assert "docs/submission.md" in read_file("README.md")


def test_report_mentions_submission_doc() -> None:
    assert "docs/submission.md" in read_file("REPORT.md")


def test_gitignore_excludes_env() -> None:
    assert ".env" in read_file(".gitignore")


def test_gitignore_excludes_db_files() -> None:
    assert "*.db" in read_file(".gitignore")


def test_dockerignore_excludes_env() -> None:
    assert ".env" in read_file(".dockerignore")


def test_dockerignore_excludes_db_files() -> None:
    assert "*.db" in read_file(".dockerignore")


def test_dockerfile_does_not_contain_sk_key_prefix() -> None:
    assert "sk-" not in read_file("Dockerfile")


def test_docker_compose_does_not_contain_sk_key_prefix() -> None:
    assert "sk-" not in read_file("docker-compose.yml")


def test_readme_does_not_contain_fake_example_public_url() -> None:
    assert "https://example.com" not in read_file("README.md")


def test_report_does_not_contain_fake_example_public_url() -> None:
    assert "https://example.com" not in read_file("REPORT.md")
