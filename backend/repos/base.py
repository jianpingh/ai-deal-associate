"""
Base Repository

Generic repository with common CRUD operations.
"""

from typing import TypeVar, Generic, Type, Optional, List
from sqlmodel import SQLModel, Session, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class with generic CRUD operations.
    
    Usage:
        class DealRepository(BaseRepository[Deal]):
            pass
        
        repo = DealRepository(Deal, session)
        deals = repo.get_all()
    """
    
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        return self.session.get(self.model, id)
    
    def get_all(self, offset: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        statement = select(self.model).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())
    
    def create(self, obj: ModelType) -> ModelType:
        """Create a new record"""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
    
    def update(self, obj: ModelType, data: dict) -> ModelType:
        """Update an existing record"""
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
    
    def delete(self, obj: ModelType) -> bool:
        """Delete a record"""
        self.session.delete(obj)
        self.session.commit()
        return True
    
    def count(self) -> int:
        """Get total count of records"""
        statement = select(self.model)
        return len(list(self.session.exec(statement).all()))
