from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

db = SessionLocal()

# 查看所有用户
users = db.query(User).all()
print(f'数据库中共有 {len(users)} 个用户')
for u in users:
    print(f'用户名: {u.username}, 邮箱: {u.email}, 是否管理员: {u.is_admin}')

# 如果没有 admin 用户，创建一个
if len(users) == 0:
    admin = User(
        username='admin',
        email='admin@example.com',
        hashed_password=get_password_hash('admin'),
        is_admin=True
    )
    db.add(admin)
    db.commit()
    print('✅ 管理员创建成功! 用户名: admin, 密码: admin')
else:
    print('用户已存在')

db.close()