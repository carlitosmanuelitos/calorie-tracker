from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, DateTime
from app.db.base import Base

class BaseModel(Base):
    """Base model for all database models with common fields"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Automatically generate table name from class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
