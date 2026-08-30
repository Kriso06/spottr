from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_]+$",
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )

class LoginRequest(BaseModel):
    email: EmailStr
    password: str 


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    bio: str | None
    is_active: bool
    verification_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)