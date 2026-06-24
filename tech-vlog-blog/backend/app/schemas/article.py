from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = Field(default=None, max_length=500)
    content_md: str = Field(..., min_length=1)
    cover_image_url: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None  # 简化：逗号分隔
    status: str = Field(default="draft")  # draft / published


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    summary: Optional[str] = Field(default=None, max_length=500)
    content_md: Optional[str] = Field(default=None, min_length=1)
    cover_image_url: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None
    status: Optional[str] = None  # draft / published


class ArticleOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    content_md: str
    cover_image_url: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None
    status: str
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

