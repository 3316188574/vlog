from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

import app.database as database
from app.database import Base
from app.schemas.common import error
from app.routers import auth, health, public_articles, admin_articles, upload, comments, categories
import app.models  # noqa: F401


def create_app(database_url: str | None = None) -> FastAPI:
    app = FastAPI(title="Tech Vlog Blog API", version="0.1.0")

    # CORS（开发阶段放开；生产建议按域名收敛）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 支持外部指定数据库（测试用）
    if database_url:
        database.init_db(database_url)

    # 初始化数据表（骨架阶段：直接 create_all；后续建议 Alembic 迁移）
    Base.metadata.create_all(bind=database.engine)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # 统一响应：HTTPException 也包装成 {code,message,data}
        if isinstance(exc.detail, dict) and {"code", "message", "data"} <= set(exc.detail.keys()):
            payload = exc.detail
        else:
            payload = error(message=str(exc.detail), code=exc.status_code)
        return JSONResponse(status_code=200, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=200, content=error(message="参数校验失败", code=422, data=exc.errors()))

    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(public_articles.router, prefix="/api")
    app.include_router(admin_articles.router, prefix="/api")
    app.include_router(upload.router, prefix="/api")
    app.include_router(comments.router, prefix="/api")
    app.include_router(categories.router, prefix="/api")

    # ========== 修改点1：使用绝对路径挂载静态文件 ==========
    # 获取当前文件所在目录的绝对路径
    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 挂载静态文件，确保图片可以通过 /uploads/ 访问
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

    # 添加根路径访问测试
    @app.get("/")
    async def root():
        return {"message": "Tech Vlog Blog API is running", "upload_dir": str(UPLOAD_DIR)}

    return app


app = create_app()