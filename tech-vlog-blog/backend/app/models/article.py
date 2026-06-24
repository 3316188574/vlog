from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(String(500), nullable=True)
    content_md = Column(Text, nullable=False)
    cover_image_url = Column(String(500), nullable=True)
    tags = Column(String(500), nullable=True)
    status = Column(String(32), default="draft", nullable=False)
    views = Column(Integer, default=0, nullable=False)  # 阅读量字段

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())