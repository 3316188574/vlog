from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Category
from app.schemas.common import ok
from app.deps import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def list_categories(
        db: Session = Depends(get_db),
):
    """获取所有分类（前台用）"""
    categories = db.query(Category).order_by(Category.name).all()
    return ok(data=[{"id": c.id, "name": c.name, "slug": c.slug} for c in categories])


@router.get("/admin/all")
def admin_list_categories(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """获取所有分类（后台用）"""
    categories = db.query(Category).order_by(Category.name).all()
    return ok(data=[{"id": c.id, "name": c.name, "slug": c.slug} for c in categories])


@router.post("/admin")
def create_category(
        name: str,
        slug: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """创建分类"""
    existing = db.query(Category).filter(
        (Category.name == name) | (Category.slug == slug)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类名称或slug已存在")

    category = Category(name=name, slug=slug)
    db.add(category)
    db.commit()
    db.refresh(category)
    return ok(data={"id": category.id, "name": category.name, "slug": category.slug})


@router.put("/admin/{category_id}")
def update_category(
        category_id: int,
        name: str,
        slug: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    category.name = name
    category.slug = slug
    db.commit()
    return ok(data={"id": category.id, "name": category.name, "slug": category.slug})


@router.delete("/admin/{category_id}")
def delete_category(
        category_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """删除分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    # 将关联的文章的分类设为 null
    from app.models import Article
    db.query(Article).filter(Article.category_id == category_id).update({"category_id": None})

    db.delete(category)
    db.commit()
    return ok(data={"id": category_id})