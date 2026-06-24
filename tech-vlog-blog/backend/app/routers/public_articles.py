from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.models.category import Category
from app.schemas.common import error, ok

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def list_articles(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=50),
        category: str | None = None,
        tag: str | None = None,
        year_month: str | None = None,
        search: str | None = None,
        db: Session = Depends(get_db),
):
    """
    文章列表（前台）
    """
    query = db.query(Article).filter(
        Article.status == "published",
        Article.published_at.isnot(None),
    )

    # 搜索功能
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.like(search_term),
                Article.content_md.like(search_term),
                Article.summary.like(search_term)
            )
        )

    # 分类筛选
    if category:
        if category.isdigit():
            query = query.filter(Article.category_id == int(category))
        else:
            query = query.join(Category, Article.category_id == Category.id).filter(
                or_(Category.slug == category, Category.name == category)
            )

    # 标签筛选
    if tag:
        query = query.filter(Article.tags.isnot(None)).filter(Article.tags.like(f"%{tag}%"))

    # 年月筛选
    if year_month is not None:
        if len(year_month) != 7 or year_month[4] != "-":
            raise HTTPException(
                status_code=422,
                detail=error(message="year_month 格式错误，应为 YYYY-MM", code=422),
            )
        try:
            year = int(year_month[:4])
            month = int(year_month[5:7])
            if month < 1 or month > 12:
                raise ValueError("month out of range")
        except Exception:
            raise HTTPException(
                status_code=422,
                detail=error(message="year_month 格式错误，应为 YYYY-MM", code=422),
            )

        query = query.filter(
            and_(
                func.strftime("%Y", Article.published_at) == str(year),
                func.strftime("%m", Article.published_at) == f"{month:02d}",
            )
        )

    total = query.count()
    items = (
        query.order_by(Article.published_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
    )

    return ok(
        data={
            "items": jsonable_encoder(items),
            "page": page,
            "page_size": page_size,
            "total": total,
            "filters": {"category": category, "tag": tag, "year_month": year_month, "search": search},
        }
    )


@router.get("/archives")
def get_archives(db: Session = Depends(get_db)):
    """获取所有有文章的年月列表"""
    results = db.query(
        func.strftime("%Y-%m", Article.published_at).label("year_month")
    ).filter(
        Article.status == "published",
        Article.published_at.isnot(None)
    ).group_by("year_month").order_by(
        func.strftime("%Y-%m", Article.published_at).desc()
    ).all()

    archives = [r[0] for r in results if r[0]]
    return ok(data=archives)


@router.get("/{article_id}")
def get_article_detail(article_id: int, db: Session = Depends(get_db)):
    """
    文章详情（前台）
    - 仅返回已发布文章（status=published）
    - 每次访问增加阅读量
    """
    article = (
        db.query(Article)
            .filter(
            Article.id == article_id,
            Article.status == "published",
        )
            .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail=error(message="文章不存在", code=404))

    # 增加阅读量
    article.views += 1
    db.commit()
    db.refresh(article)

    return ok(data=jsonable_encoder(article))