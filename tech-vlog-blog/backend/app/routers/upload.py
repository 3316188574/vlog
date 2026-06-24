import os
import shutil
from datetime import datetime
from pathlib import Path  # ← 添加这个导入
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.schemas.common import ok, error
from app.deps import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])

# ========== 修改点：使用绝对路径 ==========
# 获取 backend 目录的绝对路径
BASE_DIR = Path(__file__).resolve().parent.parent  # backend 目录
UPLOAD_DIR = BASE_DIR / "uploads"  # backend/uploads

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/image")
async def upload_image(
        file: UploadFile = File(...),
        current_user=Depends(get_current_user)
):
    """上传图片（需要登录）"""

    # 检查文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=error(message=f"不支持的文件类型，支持: {', '.join(ALLOWED_EXTENSIONS)}", code=400)
        )

    # 读取文件内容并检查大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=error(message=f"文件过大，最大 {MAX_FILE_SIZE // 1024 // 1024}MB", code=400)
        )

    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename  # ← 使用 Path 对象

    # 保存文件
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # 返回可访问的 URL
    file_url = f"/uploads/{safe_filename}"

    return ok(data={
        "url": file_url,
        "filename": safe_filename,
        "original_name": file.filename
    })


@router.get("/list")
async def list_images(
        current_user=Depends(get_current_user)
):
    """列出所有上传的图片（需要登录）"""
    images = []
    for filename in os.listdir(UPLOAD_DIR):
        if any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            file_path = UPLOAD_DIR / filename
            images.append({
                "url": f"/uploads/{filename}",
                "filename": filename,
                "size": os.path.getsize(file_path),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
    return ok(data={"images": images})


@router.delete("/image/{filename}")
async def delete_image(
        filename: str,
        current_user=Depends(get_current_user)
):
    """删除图片（需要登录）"""
    # 安全检查：防止路径穿越攻击
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail=error(message="无效的文件名", code=400))

    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=error(message="文件不存在", code=404))

    os.remove(file_path)
    return ok(message="删除成功")