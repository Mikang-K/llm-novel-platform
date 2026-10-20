import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

#프로젝트 루트의 .env 파일 로드
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.getenv("POSTGRES_HOST","127.0.0.1"),
    port=int(os.getenv("POSTGRES_PORT","5432")),
    database=os.environ["POSTGRES_DB"]
)

#DB 연결을 관리하는 핵심 개체
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
#DB 작업을 위한 세션을 만드는 팩토리
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as session:
        yield session