"""
User Repository

Data access layer for User operations.
"""

from typing import List, Optional
from sqlmodel import Session, select
from db.models import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations"""
    
    def __init__(self, session: Session):
        super().__init__(User, session)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def get_by_role(self, role: str, offset: int = 0, limit: int = 100) -> List[User]:
        """Get users filtered by role"""
        statement = select(User).where(User.role == role).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_active_users(self, offset: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        statement = select(User).where(User.is_active == True).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())
    
    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email already exists"""
        statement = select(User).where(User.email == email)
        if exclude_id:
            statement = statement.where(User.id != exclude_id)
        return self.session.exec(statement).first() is not None
