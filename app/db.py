from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


def normalized_database_url(database_url: str) -> str:
    if database_url.startswith('postgres://'):
        return database_url.replace('postgres://', 'postgresql+psycopg://', 1)
    if database_url.startswith('postgresql://') and '+psycopg' not in database_url:
        return database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return database_url


class Base(DeclarativeBase):
    pass


engine = create_engine(normalized_database_url(settings.database_url), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
