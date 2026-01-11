from sqlmodel import SQLModel
from api.database import engine
# Import models so metadata is registered
from api.models import Deal, Asset, Document, Analysis, ChatHistory

def create_db_and_tables():
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_db_and_tables()
