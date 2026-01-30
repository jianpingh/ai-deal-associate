from sqlmodel import SQLModel, create_engine
from typing import Generator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection string from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
# echo=True to see SQL queries in logs (set to False in production)
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    from sqlmodel import Session
    with Session(engine) as session:
        yield session
