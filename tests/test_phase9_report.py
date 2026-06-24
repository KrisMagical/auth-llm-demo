from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_report() -> str:
    return (PROJECT_ROOT / "REPORT.md").read_text(encoding="utf-8")


def test_report_exists() -> None:
    assert (PROJECT_ROOT / "REPORT.md").exists()


def test_report_contains_implementation_and_timeline() -> None:
    assert "实现方式以及时间规划" in read_report()


def test_report_contains_architecture() -> None:
    assert "整体架构" in read_report()


def test_report_contains_tech_stack() -> None:
    assert "技术栈" in read_report()


def test_report_contains_ai_coding() -> None:
    content = read_report()
    assert "AI Coding" in content or "AI coding" in content


def test_report_contains_token_estimate() -> None:
    content = read_report()
    assert "token" in content or "Token" in content


def test_report_contains_personal_time_section() -> None:
    assert "自己时间花最多" in read_report()


def test_report_contains_highest_priority_section() -> None:
    assert "优先级最高" in read_report()


def test_report_contains_llm_username_review() -> None:
    assert "LLM 用户名审核" in read_report()


def test_report_contains_debugging() -> None:
    assert "调试" in read_report()


def test_report_contains_optimization() -> None:
    assert "优化" in read_report()


def test_report_contains_admin_email() -> None:
    assert "admin@example.com" in read_report()


def test_report_contains_admin_password() -> None:
    assert "Admin123456" in read_report()


def test_report_contains_public_url_section() -> None:
    assert "公网访问地址" in read_report()


def test_report_public_url_is_placeholder() -> None:
    content = read_report()
    assert "待实际云平台部署完成后填写" in content


def test_readme_mentions_report() -> None:
    content = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "REPORT.md" in content
