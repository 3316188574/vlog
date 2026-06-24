from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.schemas.common import error, ok

router = APIRouter(prefix="/admin/articles", tags=["admin-articles"])


@router.get("")
def admin_list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: str | None = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Article)
    if status:
        query = query.filter(Article.status == status)

    total = query.count()
    items = (
        query.order_by(Article.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ok(
        data={
            "items": jsonable_encoder(items),
            "total": total,
            "page": page,
            "page_size": page_size,
            "current_user": current_user,
        }
    )


@router.post("")
def admin_create_article(
    payload: ArticleCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    article = Article(**payload.model_dump())
    if article.status == "published" and article.published_at is None:
        article.published_at = datetime.now(timezone.utc)

    db.add(article)
    db.commit()
    db.refresh(article)
    return ok(data=jsonable_encoder(article), message="created")


@router.put("/{article_id}")
def admin_update_article(
    article_id: int,
    payload: ArticleUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail=error(message="文章不存在", code=404))

    data = payload.model_dump(exclude_unset=True)
    old_status = article.status

    for k, v in data.items():
        setattr(article, k, v)

    # 草稿 -> 发布：补齐发布时间
    if old_status != "published" and article.status == "published" and not article.published_at:
        article.published_at = datetime.now(timezone.utc)
    # 发布 -> 草稿：可选择清空发布时间（本期选择保留，以便回滚后仍可追溯）

    db.add(article)
    db.commit()
    db.refresh(article)
    return ok(data=jsonable_encoder(article), message="updated")


@router.delete("/{article_id}")
def admin_delete_article(
    article_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail=error(message="文章不存在", code=404))
    db.delete(article)
    db.commit()
    return ok(data={"id": article_id}, message="deleted")
