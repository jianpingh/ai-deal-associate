"""
User Service

Business logic layer for User operations.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session
from db.models import User
from repos.user_repo import UserRepository
from schemas.user import UserCreate, UserUpdate


class UserService:
    """Service class for User business logic"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = UserRepository(session)
    
    def create_user(self, data: UserCreate) -> tuple[Optional[User], Optional[str]]:
        """
        Create a new user.
        Returns (user, None) on success, (None, error_message) on failure.
        """
        # Check if email already exists
        if self.repo.email_exists(data.email):
            return None, f"Email '{data.email}' already exists"
        
        # Create user
        user = User(
            email=data.email,
            name=data.name,
            role=data.role,
            # In production, hash the password
            password_hash=data.password,  # TODO: Use proper password hashing
        )
        return self.repo.create(user), None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return self.repo.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        return self.repo.get_by_email(email)
    
    def get_users(self, offset: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return self.repo.get_all(offset=offset, limit=limit)
    
    def get_users_by_role(self, role: str, offset: int = 0, limit: int = 100) -> List[User]:
        """Get users filtered by role"""
        return self.repo.get_by_role(role, offset=offset, limit=limit)
    
    def update_user(self, user_id: int, data: UserUpdate) -> tuple[Optional[User], Optional[str]]:
        """
        Update a user.
        Returns (user, None) on success, (None, error_message) on failure.
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            return None, "User not found"
        
        # Check email uniqueness if being updated
        if data.email and data.email != user.email:
            if self.repo.email_exists(data.email, exclude_id=user_id):
                return None, f"Email '{data.email}' already exists"
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        return self.repo.update(user, update_data), None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = self.repo.get_by_id(user_id)
        if not user:
            return False
        return self.repo.delete(user)
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Soft delete - deactivate a user"""
        user = self.repo.get_by_id(user_id)
        if not user:
            return None
        return self.repo.update(user, {"is_active": False, "updated_at": datetime.utcnow()})
