from sqlmodel import SQLModel, create_engine
from typing import Generator, Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection string from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine will be None if DATABASE_URL is not set
engine = None

if DATABASE_URL:
    # Create engine
    # echo=True to see SQL queries in logs (set to False in production)
    engine = create_engine(DATABASE_URL, echo=False)
else:
    print("WARNING: DATABASE_URL is not set. Database features will be disabled.")

def get_session():
    from sqlmodel import Session
    from fastapi import HTTPException
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    with Session(engine) as session:
        yield session
