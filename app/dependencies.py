"""FastAPI dependencies shared across authenticated endpoints."""

from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app import models
from app.auth import decode_access_token, oauth2_scheme
from app.database import get_db


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Return the current user from a valid bearer token."""
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception from None

    user = db.get(models.User, user_id)
    if user is None:
        raise credentials_exception

    return user


def require_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Require the current user to have the admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Resource B requires admin permission.",
        )

    return current_user
