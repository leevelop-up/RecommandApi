from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

from database import get_db, init_db
from passlib.context import CryptContext
from models import User, ProviderEnum, Watchlist, Portfolio
from schemas import (
    OAuthCallbackRequest, NaverCallbackRequest, AuthResponse, UserResponse,
    RegisterRequest, LoginRequest,
    WatchlistAddRequest, WatchlistItem,
    BuyRequest, SellRequest, PortfolioItem,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from jwt_utils import create_access_token, get_current_user
from oauth import google as google_oauth
from oauth import kakao as kakao_oauth
from oauth import naver as naver_oauth

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(
    title="Recommand Stock API",
    description="주식 추천 및 데이터 제공 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_db()


# ── 헬스체크 ────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "Recommand Stock API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ── Auth 공통 헬퍼 ──────────────────────────────────────────────────────────

def _upsert_user(db: Session, provider: ProviderEnum, user_info: dict) -> User:
    """provider + provider_id 기준으로 유저를 찾거나 생성/업데이트한다."""
    user = (
        db.query(User)
        .filter(User.provider == provider, User.provider_id == user_info["provider_id"])
        .first()
    )
    if user:
        user.name = user_info.get("name") or user.name
        user.picture = user_info.get("picture") or user.picture
    else:
        # email 중복 체크 (다른 provider로 같은 email이 있을 수 있음)
        existing = db.query(User).filter(User.email == user_info["email"]).first()
        if existing:
            user_info["email"] = f"{provider}_{user_info['provider_id']}@local"
        user = User(
            email=user_info["email"],
            name=user_info.get("name"),
            picture=user_info.get("picture"),
            provider=provider,
            provider_id=user_info["provider_id"],
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_token(user: User) -> str:
    return create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "provider": user.provider,
    })


# ── Google OAuth ─────────────────────────────────────────────────────────────

@app.post("/api/auth/google/callback", response_model=AuthResponse)
async def google_callback(body: OAuthCallbackRequest, db: Session = Depends(get_db)):
    redirect_uri = f"{FRONTEND_URL}/auth/google/callback"
    user_info = await google_oauth.exchange_code_for_user(body.code, redirect_uri)
    user = _upsert_user(db, ProviderEnum.google, user_info)
    return AuthResponse(
        success=True,
        accessToken=_make_token(user),
        user=UserResponse.model_validate(user),
    )


# ── Kakao OAuth ──────────────────────────────────────────────────────────────

@app.post("/api/auth/kakao/callback", response_model=AuthResponse)
async def kakao_callback(body: OAuthCallbackRequest, db: Session = Depends(get_db)):
    redirect_uri = os.getenv("VITE_KAKAO_REDIRECT_URI", f"{FRONTEND_URL}/auth/kakao/callback")
    user_info = await kakao_oauth.exchange_code_for_user(body.code, redirect_uri)
    user = _upsert_user(db, ProviderEnum.kakao, user_info)
    return AuthResponse(
        success=True,
        accessToken=_make_token(user),
        user=UserResponse.model_validate(user),
    )


# ── Naver OAuth ──────────────────────────────────────────────────────────────

@app.post("/api/auth/naver/callback", response_model=AuthResponse)
async def naver_callback(body: NaverCallbackRequest, db: Session = Depends(get_db)):
    user_info = await naver_oauth.exchange_code_for_user(body.code, body.state)
    user = _upsert_user(db, ProviderEnum.naver, user_info)
    return AuthResponse(
        success=True,
        accessToken=_make_token(user),
        user=UserResponse.model_validate(user),
    )


# ── 현재 유저 정보 ────────────────────────────────────────────────────────────

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == int(current_user["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return UserResponse.model_validate(user)


# ── 이메일/비밀번호 Auth ───────────────────────────────────────────────────────

@app.post("/api/auth/register", response_model=AuthResponse)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """이메일/비밀번호 회원가입"""
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
    user = User(
        email=body.email,
        name=body.name or body.email.split("@")[0],
        provider=ProviderEnum.local,
        provider_id=body.email,
        password_hash=pwd_context.hash(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(
        success=True,
        accessToken=_make_token(user),
        user=UserResponse.model_validate(user),
    )


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    """이메일/비밀번호 로그인"""
    user = db.query(User).filter(
        User.email == body.email,
        User.provider == ProviderEnum.local,
    ).first()
    if not user or not user.password_hash or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    return AuthResponse(
        success=True,
        accessToken=_make_token(user),
        user=UserResponse.model_validate(user),
    )


# ── Watchlist ─────────────────────────────────────────────────────────────────

@app.get("/api/watchlist", response_model=list[WatchlistItem])
async def get_watchlist(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """유저의 관심종목 목록 조회"""
    user_id = int(current_user["sub"])
    items = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
    return items


@app.post("/api/watchlist", response_model=WatchlistItem, status_code=201)
async def add_to_watchlist(
    body: WatchlistAddRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """관심종목 추가"""
    user_id = int(current_user["sub"])
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == user_id, Watchlist.ticker == body.ticker
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="이미 관심종목에 추가된 종목입니다.")
    item = Watchlist(user_id=user_id, ticker=body.ticker, stock_name=body.stock_name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/watchlist/{ticker}", status_code=204)
async def remove_from_watchlist(
    ticker: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """관심종목 삭제"""
    user_id = int(current_user["sub"])
    item = db.query(Watchlist).filter(
        Watchlist.user_id == user_id, Watchlist.ticker == ticker
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="관심종목에 없는 종목입니다.")
    db.delete(item)
    db.commit()


# ── Portfolio ──────────────────────────────────────────────────────────────────

@app.get("/api/portfolio", response_model=list[PortfolioItem])
async def get_portfolio(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """유저의 포트폴리오 조회"""
    user_id = int(current_user["sub"])
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).all()


@app.post("/api/portfolio/buy", response_model=PortfolioItem)
async def buy_stock(
    body: BuyRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """종목 매수 (보유량/평균단가 갱신)"""
    user_id = int(current_user["sub"])
    holding = db.query(Portfolio).filter(
        Portfolio.user_id == user_id, Portfolio.ticker == body.ticker
    ).first()
    if holding:
        total_cost = holding.avg_price * holding.quantity + body.price * body.quantity
        holding.quantity += body.quantity
        holding.avg_price = total_cost / holding.quantity
        if body.stock_name:
            holding.stock_name = body.stock_name
    else:
        holding = Portfolio(
            user_id=user_id,
            ticker=body.ticker,
            stock_name=body.stock_name,
            quantity=body.quantity,
            avg_price=body.price,
        )
        db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@app.post("/api/portfolio/sell", status_code=200)
async def sell_stock(
    body: SellRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """종목 매도 (보유량 감소, 0이 되면 삭제)"""
    user_id = int(current_user["sub"])
    holding = db.query(Portfolio).filter(
        Portfolio.user_id == user_id, Portfolio.ticker == body.ticker
    ).first()
    if not holding:
        raise HTTPException(status_code=404, detail="보유하지 않은 종목입니다.")
    if body.quantity > holding.quantity:
        raise HTTPException(status_code=400, detail="보유 수량보다 많이 매도할 수 없습니다.")
    holding.quantity -= body.quantity
    if holding.quantity == 0:
        db.delete(holding)
        db.commit()
        return {"message": "전량 매도 완료"}
    db.commit()
    db.refresh(holding)
    return PortfolioItem.model_validate(holding)


# ── 기존 API 엔드포인트 ───────────────────────────────────────────────────────

@app.get("/api/v1/stocks")
async def get_stocks(
    market: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    return {"stocks": [], "total": 0, "market": market, "limit": limit}


@app.get("/api/v1/stocks/{ticker}")
async def get_stock_detail(ticker: str):
    return {"ticker": ticker, "name": "종목명", "current_price": 0, "change": 0, "change_percent": 0}


@app.get("/api/v1/recommendations")
async def get_recommendations(
    type: Optional[str] = Query("all"),
    limit: int = Query(10, ge=1, le=100)
):
    return {"recommendations": [], "type": type, "generated_at": datetime.now().isoformat()}


@app.get("/api/v1/market/indices")
async def get_market_indices():
    return {
        "indices": [
            {"name": "KOSPI", "value": 0, "change": 0},
            {"name": "KOSDAQ", "value": 0, "change": 0},
            {"name": "NASDAQ", "value": 0, "change": 0},
        ]
    }


@app.get("/api/v1/news")
async def get_news(
    ticker: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    return {"news": [], "ticker": ticker, "total": 0}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
