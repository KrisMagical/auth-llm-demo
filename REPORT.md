# 用户登录 / 授权 Demo 说明

## 1. 实现方式以及时间规划

本项目使用 FastAPI 实现后端 API 和简单浏览器页面，使用 SQLite 保存用户数据，使用 SQLAlchemy 管理数据库模型和会话。登录态使用 JWT access token，授权模型保持轻量，只使用 `role=user` 和 `role=admin` 两种角色。注册阶段接入 LLM / mock username checker，用于判断 username 是否存在社区违规风险。

3 天时间规划如下：

第 1 天：

- 项目初始化
- 数据库和 User 模型
- 注册
- 登录
- JWT
- 资源 A/B 授权
- admin 测试账号

第 2 天：

- LLM / mock 用户名审核
- 页面交互
- README 和接口文档

第 3 天：

- REPORT 完善
- Docker 化
- 公网部署
- 最终验收

当前阶段已经完成到 REPORT 完善。Docker 化和公网部署计划在后续阶段完成，当前没有编造公网地址。

阶段 10 已完成 Docker 化准备，包括 `Dockerfile`、`.dockerignore` 和 `docker-compose.yml`。项目已支持 `docker build` / `docker run`，并支持 `docker compose up --build`。Docker 化用于后续公网部署，当前仍未完成公网部署。

阶段 11 已补充公网部署准备说明。项目可以通过 Dockerfile 在 Render 或 Railway 上构建，环境变量由云平台 Environment Variables / Variables 配置。当前 Codex 环境未直接连接云平台，因此未执行真实公网部署，也未填写真实公网 URL。

阶段 12 已新增最终验收清单 `docs/final_checklist.md` 和 smoke test 脚本 `scripts/smoke_test.py`。当前项目可以通过 pytest 和 smoke test 做最终验收。公网地址仍保留待填写，等待真实部署后更新。

阶段 13 已新增最终交付摘要 `docs/submission.md`，用于集中填写 GitHub 仓库链接、公网 URL、资源 B 测试账号和最终验证方式。

## 2. 整体架构与技术栈

整体架构由以下部分组成：

- Browser 页面：Jinja2 模板 + 原生 JavaScript fetch，方便验收人员在浏览器中操作。
- FastAPI API：提供注册、登录、当前用户、资源 A/B、用户名审核调试等接口。
- SQLite 数据库：保存用户、角色、密码哈希和 LLM 审核状态。
- JWT 认证：登录成功后签发 access token，访问受保护资源时通过 Bearer token 鉴权。
- RBAC 授权：使用 `role=user/admin` 判断资源访问权限。
- LLM / mock username checker：注册时审核 username。

核心访问流程：

1. 注册时 username 进入 checker。
2. checker 返回 allowed / rejected / uncertain / failed 或 mock 状态。
3. rejected / mock_rejected 拒绝注册，其余状态允许注册并保存审核结果。
4. 登录返回 JWT。
5. 浏览器使用 localStorage 保存 token。
6. 访问资源 A/B 时携带 Bearer token。
7. 资源 A 只要求已登录。
8. 资源 B 要求 `role=admin`。

技术栈：

- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- python-jose / JWT
- passlib[bcrypt]
- Jinja2
- OpenAI-compatible API
- pytest
- Docker，后续部署使用
- Dockerfile / docker-compose，后续公网部署使用
- Render / Railway，后续公网部署可选平台

设计出发点是优先保证题目核心验收点：注册、登录、JWT、资源 A/B 授权、资源 B 测试账号和 LLM username checker。权限链路需要清晰可验证；LLM 判断不作为强依赖，因此有 mock fallback 和 failed fallback；Demo 保持轻量，方便部署和评审。

## 3. AI Coding 工具使用情况

本项目使用 ChatGPT / Codex 辅助完成需求拆解、阶段规划、FastAPI 代码生成、测试用例补充、README/REPORT 文档整理。

Token 数为估算，不精确统计。整体大约使用 60k - 100k tokens。

最多 token 消耗在：

1. 分阶段任务拆解和验收标准设计。
2. 权限链路和 JWT 测试覆盖。
3. LLM username checker 的 prompt、fallback 和异常解析。
4. README / REPORT 文档整理。

AI Coding 工具主要用于加速实现和查漏补缺，关键需求边界、验收点和最终行为仍需要人工确认。

## 4. 自己时间花最多的部分

不计算模型生成时间，自己时间花最多的部分是需求边界确认、功能验收、联调测试和文档核对。

其中重点检查了普通用户和 admin 用户在资源 A/B 上的权限表现：

- 普通用户是否默认 `role=user`。
- 普通用户是否可以访问资源 A。
- 普通用户访问资源 B 是否稳定返回 403。
- admin 测试账号是否可以登录并访问资源 B。

LLM 审核部分重点检查了没有 API Key、mock 命中、LLM failed fallback、非法 JSON fallback 等情况。页面部分主要检查浏览器是否能完整完成注册、登录、访问资源 A/B 的流程。后续部署阶段会重点检查环境变量、Docker 启动和公网可访问性。

## 5. 该场景下优先级最高的部分

该场景下优先级最高的是认证与授权边界正确。

必须保证：

- 普通注册用户默认 `role=user`。
- 普通用户可以访问资源 A。
- 普通用户默认禁止访问资源 B。
- admin 测试账号可以访问资源 B。
- 未登录用户不能访问资源 A/B。

LLM 审核是注册链路中的辅助功能，但不能影响系统主流程稳定性。因此没有 API Key 时使用 mock checker，LLM 异常时保存 failed 并允许注册，避免外部服务波动导致 Demo 不可用。最终交付时，公网可访问和测试账号可用也是关键验收点。

## 6. LLM 用户名审核调试与优化心得

初始方案是直接让 LLM 判断 username 是否违规。这个方式实现很快，但在边界用户名上可能给出不稳定结论，例如一些看起来像品牌、官方账号或带有攻击性暗示的用户名，模型可能在 allowed 和 rejected 之间摇摆。

后续 prompt 做了几项优化：

- 改成结构化 JSON 输出。
- 要求模型只返回 JSON，不返回 Markdown 或额外解释。
- 明确只关注辱骂、仇恨、色情、暴力、违法、诈骗、钓鱼、冒充官方等风险。
- 增加 `allowed`、`rejected`、`uncertain` 三种状态。

增加 `uncertain` 的原因是避免模型在不确定样本上强行拒绝。对于 Demo 来说，过度拒绝会影响注册主流程体验，所以不确定时允许注册，但记录状态，便于后续人工复核或日志分析。

工程 fallback 也做了处理：

- 没有 `OPENAI_API_KEY` 时使用 mock checker。
- LLM 返回非法 JSON 时保存 `status=failed`。
- LLM 调用异常时保存 `status=failed`。
- `uncertain` / `failed` 允许注册但记录状态。
- 只有 `rejected` / `mock_rejected` 才拒绝注册。

mock checker 用固定敏感词表覆盖本地验收场景，例如 `official_admin` 会命中 mock 风险词并拒绝注册。这样即使没有外部 API，也可以完整演示“注册阶段进行用户名审核”的链路。

后续优化方向：

- 收集误判样本。
- 建立小型测试集。
- 调整 prompt。
- 扩展敏感词表。
- 加入人工复核。
- 对高风险 username 使用更严格策略。

## 7. 测试账号

资源 B 测试账号：

- email: `admin@example.com`
- password: `Admin123456`

说明：

- 本地默认由 seed 自动创建。
- 可通过 `ADMIN_EMAIL` / `ADMIN_PASSWORD` / `ADMIN_USERNAME` 修改。
- 普通用户默认不能访问资源 B。
- admin 用户可以访问资源 B。
- 生产部署时应修改默认密码。

## 8. 当前验收结果

当前已完成的验收结果：

- 注册普通用户成功。
- 登录普通用户成功。
- 普通用户访问资源 A 成功。
- 普通用户访问资源 B 返回 403。
- admin 登录成功。
- admin 访问资源 B 成功。
- mock 正常用户名注册成功。
- mock 违规用户名注册失败。
- 浏览器页面可完成主要流程。
- `/docs` 可访问。
- `/openapi.json` 可访问。
- 当前阶段测试已通过，pytest 当前 90 passed。
- 已新增最终验收清单和 smoke test 脚本，用于本地或公网 BASE_URL 的关键链路验证。

## 9. 公网访问地址

公网访问地址：待实际云平台部署完成后填写。

部署方式说明：

- 使用 Dockerfile 构建镜像。
- Render Web Service 可从 GitHub 仓库部署，并自动识别 Dockerfile。
- Railway 可从 GitHub 仓库部署，并根据 Dockerfile 构建。
- 生产环境变量必须通过云平台配置，不提交真实 `.env`。
- `OPENAI_API_KEY` 可选；未配置时使用 mock checker，保证 Demo 可运行。

云平台需要配置的关键环境变量：

- `JWT_SECRET=请使用强随机字符串`
- `JWT_ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- `DATABASE_URL=sqlite:///./auth_demo.db`
- `ADMIN_USERNAME=admin`
- `ADMIN_EMAIL=admin@example.com`
- `ADMIN_PASSWORD=Admin123456`
- `LLM_PROVIDER=openai`
- `OPENAI_API_KEY=可选，未配置时走 mock checker`
- `OPENAI_MODEL=gpt-4o-mini`

公网验收流程：

1. 访问首页 `/`。
2. 访问 `/health`，预期返回 `{"status":"ok"}`。
3. 访问 `/docs`，确认 API 文档可打开。
4. 注册普通用户。
5. 登录普通用户。
6. 普通用户访问资源 A，预期成功。
7. 普通用户访问资源 B，预期 403。
8. admin 登录。
9. admin 访问资源 B，预期成功。
10. 调用 `/api/debug/check-username` 检查 `official_admin`，预期 `mock_rejected` 或 LLM rejected。

## 10. 项目边界与安全说明

- 本项目是 Demo，不是生产级认证系统。
- 不实现 OAuth / SSO。
- 不实现复杂多租户权限系统。
- 只使用 `user` / `admin` 两种角色。
- SQLite 适合 Demo，生产建议换 PostgreSQL / MySQL。
- `JWT_SECRET`、`ADMIN_PASSWORD`、`OPENAI_API_KEY` 必须通过环境变量配置。
- `.env` 不应提交到 GitHub。
- 生产环境应使用 HTTPS。
- LLM 用户名审核不作为严格内容安全系统。

## DeepSeek Provider Update

The project now supports a DeepSeek provider in addition to the existing OpenAI-compatible provider and mock fallback. DeepSeek uses the same structured JSON moderation contract: `allowed`, `rejected`, or `uncertain`, plus the engineering fallback status `failed` when the provider returns invalid JSON or raises an exception.

When `LLM_PROVIDER=deepseek` and `DEEPSEEK_API_KEY` is not configured, the system falls back to the local mock checker so the Demo remains runnable without external network or paid API credentials. This update only adds provider support; it does not claim that a real DeepSeek API call has been verified in this environment.

DeepSeek environment variables:

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

No real DeepSeek API key is committed, and the public URL remains to be filled after real cloud deployment.
