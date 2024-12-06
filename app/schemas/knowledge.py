from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    category_id: int
    user_id: int
    likes: int
    created_at: datetime
    username: str  # We'll include this from the relationship

    class Config:
        from_attributes = True

class KnowledgeCategoryBase(BaseModel):
    title: str
    description: str
    content: str

class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    pass

class KnowledgeCategory(KnowledgeCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    comments: List[Comment] = []

    class Config:
        from_attributes = True
