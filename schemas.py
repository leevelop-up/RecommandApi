from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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


# ── 이메일/비밀번호 Auth ──────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# ── Watchlist ────────────────────────────────────────────────────────────────

class WatchlistAddRequest(BaseModel):
    ticker: str
    stock_name: Optional[str] = None


class WatchlistItem(BaseModel):
    id: int
    ticker: str
    stock_name: Optional[str] = None
    added_at: datetime

    class Config:
        from_attributes = True


# ── Portfolio ────────────────────────────────────────────────────────────────

class BuyRequest(BaseModel):
    ticker: str
    stock_name: Optional[str] = None
    quantity: int
    price: float


class SellRequest(BaseModel):
    ticker: str
    quantity: int
    price: float


class PortfolioItem(BaseModel):
    id: int
    ticker: str
    stock_name: Optional[str] = None
    quantity: int
    avg_price: float
    updated_at: datetime

    class Config:
        from_attributes = True
