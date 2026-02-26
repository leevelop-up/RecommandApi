from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

MARIADB_HOST = os.getenv("MARIADB_HOST", "localhost")
MARIADB_PORT = os.getenv("MARIADB_PORT", "3306")
MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "recommand_db")
MARIADB_USER = os.getenv("MARIADB_USER", "recommand_user")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "")

DATABASE_URL = (
    f"mysql+pymysql://{MARIADB_USER}:{MARIADB_PASSWORD}"
    f"@{MARIADB_HOST}:{MARIADB_PORT}/{MARIADB_DATABASE}"
    f"?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from models import User  # noqa: F401
    Base.metadata.create_all(bind=engine)
