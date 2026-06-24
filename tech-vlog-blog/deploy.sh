#!/bin/bash

# 技术博客部署脚本
# 使用方法: bash deploy.sh

echo "========================================="
echo "开始部署技术博客..."
echo "========================================="

# 设置变量
PROJECT_DIR="/var/www/tech-vlog"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 1. 拉取最新代码（如果使用 git）
# cd $PROJECT_DIR
# git pull

# 2. 安装后端依赖
echo "安装后端依赖..."
cd $BACKEND_DIR
source venv/bin/activate
pip install -r requirements.txt

# 3. 数据库迁移（如果有）
# python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# 4. 重启后端服务
echo "重启后端服务..."
sudo systemctl restart tech-vlog

# 5. 重载 Nginx
echo "重载 Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo "========================================="
echo "部署完成！"
echo "========================================="