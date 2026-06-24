# 技术 Vlog 博客系统（项目骨架）

本仓库为**可运行的项目骨架**（无具体业务逻辑），包含：
- 后端：Python + FastAPI + SQLAlchemy + SQLite（统一响应、JWT 登录占位）
- 前端：Vue 3 + Vite + Pinia + Vue Router（代理 /api、axios 自动携带 token）

---

## 目录结构

```
tech-vlog-blog/
  backend/
    app/
      routers/
      models/
      schemas/
      core/
      database.py
      deps.py
    main.py
    requirements.txt
  frontend/
    src/
      views/
      components/
      api/
      stores/
      router/
    index.html
    package.json
    vite.config.js
```

---

## 后端启动（FastAPI）

> 默认监听 `http://127.0.0.1:8000`

1) 进入后端目录
```bash
cd backend
```

2) 建议创建虚拟环境并安装依赖
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3) 启动服务
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

4) 接口自检
- 健康检查：`GET http://127.0.0.1:8000/api/health`
- Swagger：`http://127.0.0.1:8000/docs`

### 说明：统一响应格式
后端所有接口统一返回：
```json
{ "code": 0, "message": "OK", "data": {} }
```
校验/鉴权等错误也会用同样格式返回（HTTP 状态码固定为 200，靠 `code` 区分）。

### 说明：登录占位（JWT）
`POST /api/auth/login` 任意用户名/密码都会返回 token（骨架占位，后续再接入真实用户校验）。

---

## 前端启动（Vue 3 + Vite）

> 默认监听 `http://127.0.0.1:5173`，并通过 Vite 代理将 `/api` 转发到后端 `8000` 端口

1) 进入前端目录
```bash
cd frontend
```

2) 安装依赖
```bash
npm install
```

3) 启动开发服务器
```bash
npm run dev
```

4) 页面入口
- 前台占位：`http://127.0.0.1:5173/`
- 后台登录：`http://127.0.0.1:5173/login`
- 登录后进入后台占位：`http://127.0.0.1:5173/admin`

### 说明：axios 与 token
前端 `src/api/index.js` 会从 `localStorage.access_token` 读取 token，并自动加到请求头：
```
Authorization: Bearer <token>
```

---

## 下一步建议（可选）
1. 按你的 PRD/接口文档补全：文章 CRUD、分类/标签、评论、图片上传落盘/对象存储等。
2. 后端引入 Alembic 迁移与 .env 配置（JWT_SECRET_KEY 等）。
3. 前端补充后台文章管理页面（列表/编辑器/上传组件）与前台文章列表/筛选 UI。

