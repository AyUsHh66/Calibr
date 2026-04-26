from sqlmodel import create_engine, SQLModel, Session
from config import settings
import os
from pathlib import Path

# Create data directory if it doesn't exist (crucial for Render/Docker)
db_url = settings.DATABASE_URL
if "sqlite" in db_url:
    # Extract path from sqlite:///./data/calibr.db
    db_path = db_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        Path(db_dir).mkdir(parents=True, exist_ok=True)
        print(f"Database directory ensured: {db_dir}")

engine = create_engine(db_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
