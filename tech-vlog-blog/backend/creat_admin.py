"""
创建管理员用户
运行: python create_admin.py
"""
import hashlib
import secrets
from app.database import SessionLocal
from app.models import User


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = secrets.token_hex(16)
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() + ":" + salt


def create_admin():
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print(f"管理员已存在: {existing.username}")
            return

        # 创建管理员
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("✅ 管理员创建成功!")
        print("   用户名: admin")
        print("   密码: admin")
    except Exception as e:
        print(f"创建失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()