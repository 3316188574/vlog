from fastapi.testclient import TestClient

import app.database as database
from app.models.article import Article
from main import create_app


def test_admin_create_article_inserts_db_record(tmp_path):
    # 使用独立测试库文件，避免污染本地 app.db
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"

    app = create_app(database_url=db_url)
    client = TestClient(app)

    # 先登录拿 token（占位登录：任意用户名密码都可）
    login_resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin"}
    )
    login_json = login_resp.json()
    assert login_json["code"] == 0
    token = login_json["data"]["access_token"]
    assert token

    # 创建文章
    payload = {
        "title": "pytest 创建的文章",
        "summary": "summary",
        "content_md": "# hello",
        "status": "draft",
        "tags": "pytest,fastapi",
        "cover_image_url": None,
        "category_id": None,
    }
    resp = client.post(
        "/api/admin/articles",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    data = resp.json()
    assert data["code"] == 0
    assert data["message"] == "created"
    assert data["data"]["id"] is not None

    # 验证数据库确实新增记录
    session = database.SessionLocal()
    try:
        count = session.query(Article).count()
        assert count == 1
        created = session.query(Article).first()
        assert created.title == payload["title"]
    finally:
        session.close()

