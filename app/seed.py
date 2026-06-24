"""Seed data helpers."""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.models import User


load_dotenv()

logger = logging.getLogger(__name__)


def get_admin_username() -> str:
    """Return the configured admin username with a safe local fallback."""
    return os.getenv("ADMIN_USERNAME") or "admin"


def get_admin_email() -> str:
    """Return the configured admin email with a safe local fallback."""
    return os.getenv("ADMIN_EMAIL") or "admin@example.com"


def get_admin_password() -> str:
    """Return the configured admin password with a safe local fallback."""
    return os.getenv("ADMIN_PASSWORD") or "Admin123456"


def create_admin_user(db: Session) -> None:
    """Create the default admin test account if it does not already exist."""
    admin_username = get_admin_username()
    admin_email = get_admin_email()
    admin_password = get_admin_password()

    existing_user = db.query(User).filter(User.email == admin_email).first()
    if existing_user:
        if existing_user.role != "admin":
            existing_user.role = "admin"
            db.commit()
            logger.info("Updated existing admin test account role: %s", admin_email)
        else:
            logger.info("Admin test account already exists: %s", admin_email)
        return

    admin_user = User(
        username=admin_username,
        email=admin_email,
        hashed_password=get_password_hash(admin_password),
        role="admin",
        llm_status="seed",
        llm_reason="Initial admin test account for Resource B",
    )
    db.add(admin_user)
    db.commit()
    logger.info("Created admin test account: %s", admin_email)
