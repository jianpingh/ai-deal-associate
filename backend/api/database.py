from sqlmodel import SQLModel, create_engine
from typing import Generator

# Connection string provided by user
DATABASE_URL = "postgresql://neondb_owner:npg_cGf86Noprszk@ep-weathered-flower-a4je99ip-pooler.us-east-1.aws.neon.tech/gocanopt_dev?sslmode=require&channel_binding=require"

# Create engine
# echo=True to see SQL queries in logs
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    from sqlmodel import Session
    with Session(engine) as session:
        yield session
