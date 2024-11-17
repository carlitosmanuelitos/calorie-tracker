from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User, UserProfile
import os

def init_db():
    # Remove existing database if it exists
    if os.path.exists("sql_app.db"):
        os.remove("sql_app.db")
    
    # Create database engine
    SQLALCHEMY_DATABASE_URL = "sqlite:///sql_app.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
