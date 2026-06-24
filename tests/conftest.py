import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TEST_DB_PATH = PROJECT_ROOT / "test_auth_demo.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "Admin123456")
os.environ.pop("OPENAI_API_KEY", None)
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")
os.environ.setdefault("LLM_PROVIDER", "openai")

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
