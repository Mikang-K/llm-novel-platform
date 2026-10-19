import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

password = os.environ["POSTGRES_PASSWORD"]

DATABASE_URL = (
    f"postgresql+psycopg://novel:{password}"
    "@127.0.0.1:5432/novel_db"
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