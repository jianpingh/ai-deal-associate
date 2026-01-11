from sqlmodel import SQLModel, create_engine
from typing import Generator

# Connection string provided by user
DATABASE_URL = ""

# Create engine
# echo=True to see SQL queries in logs
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    from sqlmodel import Session
    with Session(engine) as session:
        yield session
