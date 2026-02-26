from sqlalchemy import Column, BigInteger, String, Enum, DateTime
from sqlalchemy.sql import func
from database import Base
import enum


class ProviderEnum(str, enum.Enum):
    google = "google"
    kakao = "kakao"
    naver = "naver"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture = Column(String(500), nullable=True)
    provider = Column(Enum(ProviderEnum), nullable=False)
    provider_id = Column(String(255), nullable=False)
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
