from sqlalchemy import Column, BigInteger, String, Enum, DateTime, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from database import Base, USE_SQLITE
import enum

# SQLite는 BigInteger auto-increment를 지원하지 않으므로 Integer 사용
_PK = Integer if USE_SQLITE else BigInteger


class ProviderEnum(str, enum.Enum):
    google = "google"
    kakao = "kakao"
    naver = "naver"
    local = "local"


class User(Base):
    __tablename__ = "users"

    id = Column(_PK, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture = Column(String(500), nullable=True)
    provider = Column(Enum(ProviderEnum), nullable=False)
    provider_id = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)  # local 로그인 전용
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "provider": self.provider,
        }


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(_PK, primary_key=True, autoincrement=True)
    user_id = Column(_PK, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(20), nullable=False)
    stock_name = Column(String(100), nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_watchlist_user_ticker"),
    )


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(_PK, primary_key=True, autoincrement=True)
    user_id = Column(_PK, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(20), nullable=False)
    stock_name = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    avg_price = Column(Float, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_portfolio_user_ticker"),
    )
