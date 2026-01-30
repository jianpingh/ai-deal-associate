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
    try:
        # Create engine with SSL settings for Neon
        # Remove channel_binding parameter if present (causes issues)
        connect_args = {"sslmode": "require"}
        engine = create_engine(
            DATABASE_URL, 
            echo=False,
            connect_args=connect_args,
            pool_pre_ping=True  # Test connection before using
        )
        print(f"INFO: Database engine created successfully")
    except Exception as e:
        print(f"ERROR: Failed to create database engine: {e}")
        engine = None
else:
    print("WARNING: DATABASE_URL is not set. Database features will be disabled.")

def get_session():
    from sqlmodel import Session
    from fastapi import HTTPException
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    with Session(engine) as session:
        yield session
