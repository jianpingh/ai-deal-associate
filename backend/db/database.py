"""
Database Connection Management

Handles database engine creation and session management.
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator, Optional
from core.config import settings

# Engine will be None if DATABASE_URL is not set
engine = None

if settings.DATABASE_URL:
    try:
        # Create engine with SSL settings for cloud databases (e.g., Neon)
        connect_args = {"sslmode": "require"} if "neon" in settings.DATABASE_URL else {}
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            connect_args=connect_args,
            pool_pre_ping=True  # Test connection before using
        )
        print("INFO: Database engine created successfully", flush=True)
    except Exception as e:
        print(f"ERROR: Failed to create database engine: {e}", flush=True)
        engine = None
else:
    print("WARNING: DATABASE_URL is not set. Database features will be disabled.", flush=True)


def init_db():
    """Initialize database tables"""
    if engine:
        SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session dependency"""
    if engine is None:
        raise RuntimeError("Database not configured")
    with Session(engine) as session:
        yield session
