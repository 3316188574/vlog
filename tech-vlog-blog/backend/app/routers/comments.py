from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Comment, Article, User
from ..schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from ..core.security import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


# ========== 前台公开接口 ==========

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        comment: CommentCreate,
        db: Session = Depends(get_db)
):
    """发表评论（公开接口）"""
    # 检查文章是否存在
    article = db.query(Article).filter(Article.id == comment.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 创建评论（默认状态为 visible）
    db_comment = Comment(
        article_id=comment.article_id,
        author_name=comment.author_name,
        author_email=comment.author_email,
        content=comment.content,
        status="visible"
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get("/article/{article_id}", response_model=List[CommentResponse])
async def get_article_comments(
        article_id: int,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db)
):
    """获取文章的所有可见评论"""
    comments = db.query(Comment).filter(
        Comment.article_id == article_id,
        Comment.status == "visible"
    ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()
    return comments


@router.get("/article/{article_id}/count")
async def get_comment_count(
        article_id: int,
        db: Session = Depends(get_db)
):
    """获取文章的评论数量"""
    count = db.query(Comment).filter(
        Comment.article_id == article_id,
        Comment.status == "visible"
    ).count()
    return {"count": count}


# ========== 后台管理接口（需要登录） ==========

@router.get("/admin/all", response_model=List[CommentResponse])
async def get_all_comments(
        status: Optional[str] = Query(None, regex="^(visible|hidden)$"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取所有评论（后台）"""
    query = db.query(Comment)
    if status:
        query = query.filter(Comment.status == status)
    comments = query.order_by(Comment.created_at.desc()).all()
    return comments


@router.put("/admin/{comment_id}", response_model=CommentResponse)
async def update_comment(
        comment_id: int,
        comment_update: CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """更新评论（审核/隐藏/编辑内容）"""
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    update_data = comment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_comment, field, value)

    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.delete("/admin/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """删除评论"""
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    db.delete(db_comment)
    db.commit()
    return None


@router.post("/admin/{comment_id}/toggle-status")
async def toggle_comment_status(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """切换评论状态（显示/隐藏）"""
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    db_comment.status = "hidden" if db_comment.status == "visible" else "visible"
    db.commit()

    return {
        "id": comment_id,
        "status": db_comment.status,
        "message": f"评论已{'隐藏' if db_comment.status == 'hidden' else '显示'}"
    }


from fastapi import Request
from ..models import Like


@router.post("/{comment_id}/like")
async def like_comment(
        comment_id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """点赞/取消点赞评论"""
    # 获取客户端IP
    ip_address = request.client.host

    # 检查是否已经点过赞
    existing_like = db.query(Like).filter(
        Like.comment_id == comment_id,
        Like.ip_address == ip_address
    ).first()

    if existing_like:
        # 取消点赞
        db.delete(existing_like)
        db.commit()
        like_count = db.query(Like).filter(Like.comment_id == comment_id).count()
        return {"liked": False, "like_count": like_count}
    else:
        # 添加点赞
        new_like = Like(comment_id=comment_id, ip_address=ip_address)
        db.add(new_like)
        db.commit()
        like_count = db.query(Like).filter(Like.comment_id == comment_id).count()
        return {"liked": True, "like_count": like_count}


@router.get("/{comment_id}/like-count")
async def get_like_count(comment_id: int, db: Session = Depends(get_db)):
    """获取评论点赞数"""
    count = db.query(Like).filter(Like.comment_id == comment_id).count()
    return {"like_count": count}