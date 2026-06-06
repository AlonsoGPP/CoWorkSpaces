import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/cowork_reservations"
)


def build_engine(database_url: str | None = None) -> Engine:
    resolved_database_url = database_url or os.getenv(
        "DATABASE_URL", DEFAULT_DATABASE_URL
    )
    return create_engine(resolved_database_url, pool_pre_ping=True)


def build_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    engine = build_engine(database_url)
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )
