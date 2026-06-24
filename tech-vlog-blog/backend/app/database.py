import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# 全局默认（可在测试中通过 init_db 覆盖）
engine = None
SessionLocal = None


def init_db(database_url: str | None = None):
    """
    初始化数据库连接（骨架/测试友好）。
    - 默认使用环境变量 DATABASE_URL，否则落到 sqlite:///./app.db
    """
    global engine, SessionLocal

    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./app.db")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}

    engine = create_engine(url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine


# 模块导入时先初始化一次（默认 app.db）
init_db()


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
