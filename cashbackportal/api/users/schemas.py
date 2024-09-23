from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field


class SignInRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SignUpRequest(SignInRequest):
    name: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    expires_at: AwareDatetime


class UserResponse(BaseModel):
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
