from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # Only needed for SQLite — removes threading restriction
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency — injects a DB session into each route, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
