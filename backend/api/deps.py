"""
API Dependencies

Dependency injection helpers for FastAPI routes.
"""

from typing import Generator
from sqlmodel import Session
from db.database import get_session


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    yield from get_session()
