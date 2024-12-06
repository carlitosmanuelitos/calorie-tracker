from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class KnowledgeCategory(Base):
    """Knowledge category model for storing fitness and nutrition articles"""
    __tablename__ = "knowledge_categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Main article content
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship with comments
    comments = relationship("Comment", back_populates="category")

class Comment(Base):
    """Comment model for knowledge base articles"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("KnowledgeCategory", back_populates="comments")
    user = relationship("User", back_populates="comments")
