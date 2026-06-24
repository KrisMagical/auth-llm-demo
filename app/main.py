"""FastAPI entrypoint for auth-llm-demo."""

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.auth import create_access_token, get_password_hash, verify_password
from app.database import Base, SessionLocal, engine, get_db
from app.dependencies import get_current_user, require_admin
from app.llm_guard import check_username
from app.schemas import (
    RegisterResponse,
    ResourceResponse,
    ResourceUserInfo,
    Token,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.seed import create_admin_user, get_admin_email


app = FastAPI(title="auth-llm-demo")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables and seed the admin account."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_admin_user(db)
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse, tags=["pages"], summary="Home page")
def read_root(request: Request) -> HTMLResponse:
    """Render the demo homepage."""
    return templates.TemplateResponse(request, "index.html")


@app.get(
    "/register",
    response_class=HTMLResponse,
    tags=["pages"],
    summary="Registration page",
)
def read_register_page(request: Request) -> HTMLResponse:
    """Render the registration page."""
    return templates.TemplateResponse(request, "register.html")


@app.get("/login", response_class=HTMLResponse, tags=["pages"], summary="Login page")
def read_login_page(request: Request) -> HTMLResponse:
    """Render the login page."""
    return templates.TemplateResponse(request, "login.html")


@app.get(
    "/me",
    response_class=HTMLResponse,
    tags=["pages"],
    summary="Current user page",
)
def read_me_page(request: Request) -> HTMLResponse:
    """Render the current user page."""
    return templates.TemplateResponse(request, "me.html")


@app.get(
    "/resource-a",
    response_class=HTMLResponse,
    tags=["pages"],
    summary="Resource A page",
)
def read_resource_a_page(request: Request) -> HTMLResponse:
    """Render the Resource A page."""
    return templates.TemplateResponse(request, "resource_a.html")


@app.get(
    "/resource-b",
    response_class=HTMLResponse,
    tags=["pages"],
    summary="Resource B page",
)
def read_resource_b_page(request: Request) -> HTMLResponse:
    """Render the Resource B page."""
    return templates.TemplateResponse(request, "resource_b.html")


@app.get(
    "/demo-accounts",
    response_class=HTMLResponse,
    tags=["pages"],
    summary="Demo accounts page",
)
def read_demo_accounts_page(request: Request) -> HTMLResponse:
    """Render the demo accounts page."""
    return templates.TemplateResponse(request, "demo_accounts.html")


@app.get(
    "/debug-username",
    response_class=HTMLResponse,
    tags=["pages"],
    summary="Username checker debug page",
)
def read_debug_username_page(request: Request) -> HTMLResponse:
    """Render the username checker debug page."""
    return templates.TemplateResponse(request, "debug_username.html")


@app.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Health check endpoint used for local and deployment verification."""
    return {"status": "ok"}


@app.get("/debug/users/count", tags=["debug"], summary="Debug user count")
def debug_users_count() -> dict[str, int]:
    """Temporary development endpoint to verify database and seed state."""
    db: Session = SessionLocal()
    try:
        return {"count": db.query(models.User).count()}
    finally:
        db.close()


@app.get("/api/demo-accounts", tags=["demo"], summary="Demo account guidance")
def read_demo_accounts() -> dict[str, dict[str, object]]:
    """Return non-sensitive demo account guidance."""
    return {
        "resource_b_test_account": {
            "email": get_admin_email(),
            "password_hint": (
                "Configured by ADMIN_PASSWORD environment variable. "
                "Default for local demo: Admin123456"
            ),
            "role": "admin",
            "can_access": ["resource-a", "resource-b"],
        },
        "normal_user_rule": {
            "role": "user",
            "can_access": ["resource-a"],
            "cannot_access": ["resource-b"],
        },
    }


@app.post(
    "/api/debug/check-username",
    tags=["debug"],
    summary="Debug username moderation",
)
def debug_check_username(payload: dict[str, str]) -> dict[str, str]:
    """Development endpoint for checking username moderation behavior."""
    username = payload.get("username", "")
    return check_username(username)


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Return a user by email if one exists."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_registered_user(
    db: Session,
    payload: UserCreate,
    username_check: dict[str, str],
) -> models.User:
    """Create a normal user account for the registration flow."""
    user = models.User(
        username=payload.username,
        email=str(payload.email),
        hashed_password=get_password_hash(payload.password),
        role="user",
        llm_status=username_check["status"],
        llm_reason=username_check["reason"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post(
    "/api/register",
    response_model=RegisterResponse,
    tags=["auth"],
    summary="Register a new user",
)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> RegisterResponse:
    """Register a normal user after username moderation."""
    if get_user_by_email(db, str(payload.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    username_check = check_username(payload.username)
    if username_check["status"] in {"rejected", "mock_rejected"}:
        raise HTTPException(
            status_code=400,
            detail=f"Username rejected: {username_check['reason']}",
        )

    user = create_registered_user(db, payload, username_check)
    return RegisterResponse(message="registered successfully", user=user)


@app.post(
    "/api/login",
    response_model=Token,
    tags=["auth"],
    summary="Login and issue JWT access token",
)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Authenticate a user and return a JWT access token."""
    user = get_user_by_email(db, str(payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    return Token(access_token=access_token)


@app.get(
    "/api/me",
    response_model=UserRead,
    tags=["auth"],
    summary="Get current user",
)
def read_current_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Return the authenticated user's public profile."""
    return current_user


@app.get(
    "/api/resource-a",
    response_model=ResourceResponse,
    tags=["resources"],
    summary="Access Resource A",
)
def read_resource_a(
    current_user: models.User = Depends(get_current_user),
) -> ResourceResponse:
    """Return Resource A for any authenticated user."""
    return ResourceResponse(
        resource="A",
        message="This is Resource A. All authenticated users can access it.",
        user=ResourceUserInfo(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role,
        ),
    )


@app.get(
    "/api/resource-b",
    response_model=ResourceResponse,
    tags=["resources"],
    summary="Access Resource B",
)
def read_resource_b(
    current_user: models.User = Depends(require_admin),
) -> ResourceResponse:
    """Return Resource B only for admin users."""
    return ResourceResponse(
        resource="B",
        message="This is Resource B. Only admin users can access it.",
        user=ResourceUserInfo(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role,
        ),
    )
