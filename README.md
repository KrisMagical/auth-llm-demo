# Auth LLM Demo

## 1. 项目简介

Auth LLM Demo 是一个用户注册 / 登录 / 授权 Demo。项目支持注册、登录、JWT 认证，并提供两类受保护资源：

- 资源 A：所有登录用户可访问。
- 资源 B：仅 admin 测试账号可访问。

注册时会接入 LLM / mock username checker 判断用户名是否存在社区违规风险。项目同时提供简单浏览器页面和 REST API，方便评审者不用 Postman 也能完成验收。

## 2. 题目要求覆盖情况

| 要求 | 实现情况 |
|---|---|
| 可注册 / 登录 | 已实现 |
| 默认授权用户访问资源 A | 已实现，所有登录用户可访问 |
| 默认禁止用户访问资源 B | 已实现，普通 user 返回 403 |
| 提供可访问资源 B 的测试账号 | 已实现，admin@example.com / Admin123456 |
| 注册时引入 LLM 判断注册名是否社区违规 | 已实现，支持 OpenAI-compatible API 和 mock fallback |
| Markdown 说明调试 / 优化心得 | REPORT.md 中说明 |
| 公网 URL | 后续部署阶段填写 |

## 3. 技术栈

- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- JWT / python-jose
- passlib[bcrypt]
- Jinja2
- OpenAI-compatible LLM API
- Docker，后续部署阶段使用
- pytest

## 4. 功能列表

- 用户注册
- 用户登录
- JWT access token
- 当前用户查询
- 资源 A
- 资源 B
- admin 测试账号 seed
- LLM / mock 用户名审核
- 浏览器页面
- API 文档 `/docs`

`REPORT.md` 包含实现方式、时间规划、AI coding 工具使用、token 估算和 LLM 审核调试心得。

`docs/submission.md` 是最终交付摘要，包含仓库链接、公网 URL、资源 B 测试账号和验证方式的待填写模板。

## 5. 快速开始：本地运行

创建虚拟环境：

```bash
python -m venv .venv
```

Windows 激活：

```bash
.venv\Scripts\activate
```

macOS / Linux 激活：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

复制环境变量：

```bash
cp .env.example .env
```

启动服务：

```bash
uvicorn app.main:app --reload
```

访问：

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

## 6. 环境变量说明

| 变量 | 默认值 | 说明 |
|---|---|---|
| JWT_SECRET | change-me | JWT 签名密钥 |
| JWT_ALGORITHM | HS256 | JWT 算法 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 60 | token 过期时间 |
| DATABASE_URL | sqlite:///./auth_demo.db | 数据库地址 |
| ADMIN_USERNAME | admin | 管理员用户名 |
| ADMIN_EMAIL | admin@example.com | 资源 B 测试账号邮箱 |
| ADMIN_PASSWORD | Admin123456 | 资源 B 测试账号密码 |
| LLM_PROVIDER | openai | LLM provider |
| OPENAI_API_KEY | 空 / your-openai-api-key | OpenAI-compatible API Key |
| OPENAI_MODEL | gpt-4o-mini | 模型名称 |

安全说明：

- 不要提交 `.env`。
- 不要把 `OPENAI_API_KEY` 写死在代码里。
- 生产环境应修改 `JWT_SECRET` 和 `ADMIN_PASSWORD`。

## 7. 测试账号

资源 B 测试账号：

- email: `admin@example.com`
- password: `Admin123456`

说明：

- 本地默认 seed 自动创建。
- 生产部署可通过 `ADMIN_EMAIL` / `ADMIN_PASSWORD` 修改。
- 普通注册用户默认 `role=user`，只能访问资源 A，不能访问资源 B。

## 8. 浏览器验收流程

1. 打开首页：

```text
http://127.0.0.1:8000/
```

2. 注册普通用户：`/register`

示例：

```text
username: normal_user
email: normal@example.com
password: User123456
```

3. 登录普通用户：`/login`

4. 访问资源 A：`/resource-a`

预期成功。

5. 访问资源 B：`/resource-b`

普通用户预期 `403`。

6. 登录 admin：

```text
email: admin@example.com
password: Admin123456
```

7. 再访问资源 B：`/resource-b`

预期成功。

8. 用户名审核调试：`/debug-username`

输入 `official_admin`，预期 `mock_rejected`。

页面使用 `localStorage` 保存 JWT access token。

## 9. API 说明

| Method | Path | 说明 | 鉴权 |
|---|---|---|---|
| GET | /health | 健康检查 | 否 |
| POST | /api/register | 注册 | 否 |
| POST | /api/login | 登录 | 否 |
| GET | /api/me | 当前用户 | Bearer token |
| GET | /api/resource-a | 资源 A | Bearer token |
| GET | /api/resource-b | 资源 B | admin Bearer token |
| GET | /api/demo-accounts | 测试账号说明 | 否 |
| POST | /api/debug/check-username | 用户名审核调试 | 否 |
| GET | /debug/users/count | 开发调试用户数 | 否，后续可删除 |

## 10. curl 示例

注册普通用户：

```bash
curl -X POST http://127.0.0.1:8000/api/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"normal_user\",\"email\":\"normal@example.com\",\"password\":\"User123456\"}"
```

登录普通用户：

```bash
curl -X POST http://127.0.0.1:8000/api/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"normal@example.com\",\"password\":\"User123456\"}"
```

访问当前用户：

```bash
curl http://127.0.0.1:8000/api/me \
  -H "Authorization: Bearer <access_token>"
```

普通用户访问资源 A：

```bash
curl http://127.0.0.1:8000/api/resource-a \
  -H "Authorization: Bearer <user_access_token>"
```

普通用户访问资源 B，预期 `403`：

```bash
curl http://127.0.0.1:8000/api/resource-b \
  -H "Authorization: Bearer <user_access_token>"
```

admin 登录：

```bash
curl -X POST http://127.0.0.1:8000/api/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@example.com\",\"password\":\"Admin123456\"}"
```

admin 访问资源 B：

```bash
curl http://127.0.0.1:8000/api/resource-b \
  -H "Authorization: Bearer <admin_access_token>"
```

用户名审核调试：

```bash
curl -X POST http://127.0.0.1:8000/api/debug/check-username \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"official_admin\"}"
```

## 11. LLM 配置说明

本项目注册时会调用 username checker。

如果配置：

```env
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
LLM_PROVIDER=openai
```

则使用真实 OpenAI-compatible LLM。

如果没有配置 `OPENAI_API_KEY`：

- 自动使用 mock checker。
- 命中 mock 风险词时返回 `mock_rejected`。
- 未命中时返回 `mock_allowed`。
- 这样保证 Demo 无外部 API 也能运行。

审核策略：

- `rejected` / `mock_rejected`：拒绝注册。
- `allowed` / `mock_allowed`：允许注册。
- `uncertain`：允许注册并记录状态。
- `failed`：允许注册并记录状态，避免 LLM 异常影响主流程。

## 12. 页面路由说明

| Path | 说明 |
|---|---|
| / | 首页 |
| /register | 注册页 |
| /login | 登录页 |
| /me | 当前用户页 |
| /resource-a | 资源 A 页面 |
| /resource-b | 资源 B 页面 |
| /demo-accounts | 测试账号说明 |
| /debug-username | 用户名审核调试页 |
| /docs | FastAPI API 文档 |

## 13. 安全边界说明

1. 本项目是 Demo，不是生产级认证系统。
2. 不实现 OAuth / SSO。
3. 不实现复杂多租户 RBAC。
4. 只使用 `user` / `admin` 两种角色。
5. `JWT_SECRET`、`ADMIN_PASSWORD`、`OPENAI_API_KEY` 必须通过环境变量配置。
6. `.env` 不应提交到 GitHub。
7. 真实生产环境应使用 HTTPS、强密码、持久化数据库、日志审计和更严格的权限管理。
8. LLM 用户名审核只是演示接入链路，不作为严格内容安全系统。

## 14. 开发调试说明

- `/debug/users/count` 是开发阶段调试接口，后续生产可删除。
- `/api/debug/check-username` 是 LLM / mock 审核调试接口，生产可加鉴权或删除。
- SQLite 适合 Demo，生产建议换成 PostgreSQL / MySQL。

## 15. 测试

```bash
pytest
```

## 15.1 最终验收

最终交付前可按 [docs/final_checklist.md](docs/final_checklist.md) 逐项检查。

本地 smoke test：

```bash
uvicorn app.main:app --reload
python scripts/smoke_test.py
```

公网 smoke test：

```bash
BASE_URL=https://your-public-url python scripts/smoke_test.py
```

Windows PowerShell：

```powershell
$env:BASE_URL="https://your-public-url"
python scripts/smoke_test.py
```

Smoke test 覆盖：

- health
- 注册
- 登录
- 资源 A
- 普通用户资源 B 403
- admin 资源 B 200
- mock 用户名审核

## 16. Docker 运行

准备环境变量：

```bash
cp .env.example .env
```

Windows PowerShell 可手动复制：

```powershell
copy .env.example .env
```

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
http://127.0.0.1:8000/docs
```

Docker Compose 运行：

```bash
docker compose up --build
```

停止：

```bash
docker compose down
```

清除 volume：

```bash
docker compose down -v
```

Docker 启动后验证：

```bash
curl http://127.0.0.1:8000/health
```

注册普通用户：

```bash
curl -X POST http://127.0.0.1:8000/api/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"docker_user\",\"email\":\"docker_user@example.com\",\"password\":\"User123456\"}"
```

登录 admin：

```bash
curl -X POST http://127.0.0.1:8000/api/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@example.com\",\"password\":\"Admin123456\"}"
```

admin 访问资源 B：

```bash
curl http://127.0.0.1:8000/api/resource-b \
  -H "Authorization: Bearer <admin_access_token>"
```

`.dockerignore` 会排除 `.env`、本地 SQLite 数据库和测试缓存，避免敏感配置或本地数据进入镜像。

## 17. 公网部署准备

部署前需要将代码推送到 GitHub，并在云平台中通过 Environment Variables / Variables 配置环境变量。不要提交真实 `.env`，不要把 `OPENAI_API_KEY`、生产 `JWT_SECRET` 或生产 admin 密码写进代码。

云平台环境变量清单：

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

说明：

- 如果不配置 `OPENAI_API_KEY`，系统仍可运行，注册时使用 mock checker。
- 最终演示为了稳定，可以不配置真实 LLM Key，使用 mock fallback。
- 如果配置真实 `OPENAI_API_KEY`，不要写入代码或提交到 GitHub。
- 生产部署应把 `JWT_SECRET` 和 `ADMIN_PASSWORD` 改成更强的值。
- 如果为了交付方便使用默认 admin 密码，需要明确说明这是 Demo 测试账号。

更多部署细节见 [docs/deployment.md](docs/deployment.md)。

## 18. Render 部署

1. 将代码推送到 GitHub。
2. 打开 Render。
3. New + 选择 Web Service。
4. 连接 GitHub 仓库。
5. Runtime / Environment 选择 Docker，或让平台自动识别 `Dockerfile`。
6. 配置环境变量。
7. Deploy。
8. 部署完成后访问平台提供的公网 URL。

部署后验证：

```text
https://<your-render-service>.onrender.com/
https://<your-render-service>.onrender.com/health
https://<your-render-service>.onrender.com/docs
```

当前阶段如果没有真实部署，不要写假 URL。上面的地址只是占位格式。

## 19. Railway 部署

1. 将代码推送到 GitHub。
2. 打开 Railway。
3. New Project。
4. Deploy from GitHub Repo。
5. 选择当前仓库。
6. Railway 会根据 `Dockerfile` 构建。
7. 配置 Variables。
8. Generate Domain。
9. 使用 Railway 提供的公网域名访问。

部署后验证：

```text
https://<your-railway-domain>/
https://<your-railway-domain>/health
https://<your-railway-domain>/docs
```

当前阶段如果没有真实部署，不要写假 URL。上面的地址只是占位格式。

## 20. 公网部署验收清单

设置公网地址：

```bash
export BASE_URL=https://your-public-url
```

Windows PowerShell：

```powershell
$env:BASE_URL="https://your-public-url"
```

首页：

```bash
curl $BASE_URL/
```

健康检查：

```bash
curl $BASE_URL/health
```

API 文档：

```text
$BASE_URL/docs
```

注册普通用户：

```bash
curl -X POST $BASE_URL/api/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"public_user\",\"email\":\"public_user@example.com\",\"password\":\"User123456\"}"
```

登录普通用户：

```bash
curl -X POST $BASE_URL/api/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"public_user@example.com\",\"password\":\"User123456\"}"
```

普通用户访问资源 A，预期 `200`：

```bash
curl $BASE_URL/api/resource-a \
  -H "Authorization: Bearer <user_access_token>"
```

普通用户访问资源 B，预期 `403`：

```bash
curl $BASE_URL/api/resource-b \
  -H "Authorization: Bearer <user_access_token>"
```

admin 登录：

```bash
curl -X POST $BASE_URL/api/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@example.com\",\"password\":\"Admin123456\"}"
```

admin 访问资源 B，预期 `200`：

```bash
curl $BASE_URL/api/resource-b \
  -H "Authorization: Bearer <admin_access_token>"
```

mock 用户名审核，预期 `mock_rejected`：

```bash
curl -X POST $BASE_URL/api/debug/check-username \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"official_admin\"}"
```

## 21. 部署故障排查

- Docker daemon 未启动：先启动 Docker Desktop，再执行 `docker build`。
- `PORT` 变量未正确读取：确认云平台已设置 `PORT` 或使用平台自动注入的端口。
- `.env` 未配置：本地运行需复制 `.env.example` 到 `.env`，云平台需配置 Environment Variables / Variables。
- `OPENAI_API_KEY` 未配置：系统会走 mock checker，这是预期行为。
- SQLite 在部分免费云平台重启后可能丢失本地数据：生产建议使用托管 PostgreSQL / MySQL。
- admin 密码生产环境应修改：不要长期使用 `Admin123456`。
- `/docs` 可用于快速验收 API 是否启动成功。

## DeepSeek API Support

DeepSeek API is OpenAI-compatible, so this project calls it with the same `openai` Python SDK used by the OpenAI provider.

Use these environment variables when you want username moderation to use DeepSeek:

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

Notes:
- Do not write `DEEPSEEK_API_KEY` into code or commit it to GitHub.
- If `DEEPSEEK_API_KEY` is missing, the app automatically falls back to the local mock checker.
- `deepseek-chat` is suitable for this username moderation Demo.
- `deepseek-reasoner` is a reasoning model and is not the first choice for this simple structured moderation task.

Render environment variable example:

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```
