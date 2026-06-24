"""Pydantic schemas for users and auth responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Input schema for user registration."""

    username: str = Field(min_length=2, max_length=32)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Input schema reserved for the later login endpoint."""

    email: EmailStr
    password: str


class UserRead(BaseModel):
    """Public user fields safe to return from API responses."""

    id: int
    username: str
    email: EmailStr
    role: str
    llm_status: str | None = None
    llm_reason: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT response shape reserved for the later login endpoint."""

    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Response returned after a successful registration."""

    message: str
    user: UserRead


class ResourceUserInfo(BaseModel):
    """Minimal user information returned from resource endpoints."""

    id: int
    email: EmailStr
    role: str


class ResourceResponse(BaseModel):
    """Response shape for protected demo resources."""

    resource: str
    message: str
    user: ResourceUserInfo
