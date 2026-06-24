# Deployment Guide

本文档用于 auth-llm-demo 的 Docker、Render 和 Railway 部署准备。当前阶段未执行真实公网部署，不包含真实公网 URL。

## Docker 部署

构建镜像：

```bash
docker build -t auth-llm-demo .
```

运行容器：

```bash
docker run --rm -p 8000:8000 --env-file .env auth-llm-demo
```

访问：

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Render 部署

1. 将代码推送到 GitHub。
2. 打开 Render。
3. New + 选择 Web Service。
4. 连接 GitHub 仓库。
5. Runtime / Environment 选择 Docker，或让 Render 自动识别 Dockerfile。
6. 配置 Environment Variables。
7. Deploy。
8. 使用 Render 提供的公网 URL 验收。

占位格式：

```text
https://<your-render-service>.onrender.com
```

## Railway 部署

1. 将代码推送到 GitHub。
2. 打开 Railway。
3. New Project。
4. Deploy from GitHub Repo。
5. 选择当前仓库。
6. Railway 根据 Dockerfile 构建。
7. 配置 Variables。
8. Generate Domain。
9. 使用 Railway 提供的公网域名验收。

占位格式：

```text
https://<your-railway-domain>
```

## 环境变量

云平台需要通过 Environment Variables / Variables 配置：

```env
JWT_SECRET=请使用强随机字符串
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./auth_demo.db

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin123456

LLM_PROVIDER=openai
OPENAI_API_KEY=可选，未配置时走 mock checker
OPENAI_MODEL=gpt-4o-mini
```

不要提交真实 `.env`，不要把真实 `OPENAI_API_KEY` 写入代码。

## 公网验收

假设公网地址为：

```bash
export BASE_URL=https://your-public-url
```

需要验证：

- `GET $BASE_URL/`
- `GET $BASE_URL/health`
- `GET $BASE_URL/docs`
- 普通用户注册 / 登录
- 普通用户访问资源 A 返回 200
- 普通用户访问资源 B 返回 403
- admin 登录
- admin 访问资源 B 返回 200
- `/api/debug/check-username` 输入 `official_admin` 返回 `mock_rejected` 或 LLM rejected

## 常见问题

- Docker daemon 未启动：启动 Docker Desktop。
- `PORT` 变量异常：确认 Dockerfile 使用 `${PORT}`，云平台正确注入或设置端口。
- `OPENAI_API_KEY` 未配置：系统使用 mock checker。
- SQLite 数据丢失：免费云平台文件系统可能非持久化，生产建议使用 PostgreSQL / MySQL。
- admin 默认密码：Demo 可用，生产应修改 `ADMIN_PASSWORD`。
