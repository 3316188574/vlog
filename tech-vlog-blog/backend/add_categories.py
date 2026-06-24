"""
添加分类数据
运行: python add_categories.py
"""
from app.database import SessionLocal
from app.models import Category


def add_categories():
    db = SessionLocal()
    try:
        categories = ['嵌入式']
        added_count = 0

        for name in categories:
            existing = db.query(Category).filter(Category.name == name).first()
            if not existing:
                slug = name.lower().replace(' ', '-')
                category = Category(name=name, slug=slug)
                db.add(category)
                added_count += 1
                print(f'✅ 添加分类: {name}')
            else:
                print(f'⏭️ 分类已存在: {name}')

        db.commit()
        print(f'\n🎉 完成！共添加 {added_count} 个新分类')
    except Exception as e:
        print(f'❌ 添加失败: {e}')
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_categories()