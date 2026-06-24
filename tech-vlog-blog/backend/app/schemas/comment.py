from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CommentBase(BaseModel):
    article_id: int
    author_name: str
    author_email: Optional[EmailStr] = None
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    status: Optional[str] = None  # visible / hidden
    content: Optional[str] = None


class CommentResponse(BaseModel):
    id: int
    article_id: int
    author_name: str
    author_email: Optional[str] = None
    content: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True