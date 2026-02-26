from pydantic import BaseModel
from typing import Optional


class OAuthCallbackRequest(BaseModel):
    code: str


class NaverCallbackRequest(BaseModel):
    code: str
    state: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    success: bool
    accessToken: Optional[str] = None
    user: Optional[UserResponse] = None
    error: Optional[str] = None
