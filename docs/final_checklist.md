# Final Checklist

## 1. 本地运行验收

- [ ] 创建虚拟环境
- [ ] 安装依赖
- [ ] 复制 .env.example 为 .env
- [ ] 启动 uvicorn app.main:app --reload
- [ ] 首页 / 可访问
- [ ] /health 返回 {"status":"ok"}
- [ ] /docs 可访问
- [ ] /openapi.json 可访问

## 2. 注册 / 登录验收

- [ ] 普通用户可以注册
- [ ] 重复 email 注册失败
- [ ] 密码不会明文保存
- [ ] 登录成功返回 bearer token
- [ ] 错误密码登录失败
- [ ] /api/me 携带 token 返回当前用户
- [ ] /api/me 不返回 hashed_password

## 3. 资源 A / B 授权验收

- [ ] 未登录访问资源 A 返回 401
- [ ] 未登录访问资源 B 返回 401
- [ ] 普通用户访问资源 A 返回 200
- [ ] 普通用户访问资源 B 返回 403
- [ ] admin 用户访问资源 A 返回 200
- [ ] admin 用户访问资源 B 返回 200
- [ ] 响应不返回 hashed_password

## 4. 资源 B 测试账号验收

email: admin@example.com
password: Admin123456

- [ ] admin seed 自动创建
- [ ] admin 可以登录
- [ ] admin 可以访问资源 B
- [ ] 普通用户不能通过注册传 role=admin 提权
- [ ] 生产环境应修改 ADMIN_PASSWORD

## 5. LLM / mock 用户名审核验收

- [ ] 未配置 OPENAI_API_KEY 时走 mock checker
- [ ] normal_user 注册成功，llm_status=mock_allowed
- [ ] official_admin 注册失败，返回 400
- [ ] /api/debug/check-username 可返回 mock_rejected
- [ ] failed / uncertain 不阻断注册
- [ ] API Key 不写死在代码中
- [ ] .env 不提交到 GitHub

## 6. 浏览器页面验收

- [ ] /register 可注册
- [ ] /login 可登录
- [ ] /me 可查看当前用户
- [ ] /resource-a 普通用户可访问
- [ ] /resource-b 普通用户显示 403
- [ ] /resource-b admin 可访问
- [ ] /demo-accounts 显示测试账号说明
- [ ] /debug-username 可调试用户名审核

## 7. Docker 验收

- [ ] Dockerfile 存在
- [ ] .dockerignore 排除 .env 和 *.db
- [ ] docker build -t auth-llm-demo . 成功
- [ ] docker run --rm -p 8000:8000 --env-file .env auth-llm-demo 成功
- [ ] 容器内 /health 正常
- [ ] docker compose up --build 成功
- [ ] docker compose down 可停止服务

说明：如果 Docker daemon 未运行，需要先启动 Docker Desktop。

## 8. 公网部署验收

使用 BASE_URL：

- [ ] BASE_URL/ 可访问
- [ ] BASE_URL/health 正常
- [ ] BASE_URL/docs 可访问
- [ ] 公网注册普通用户成功
- [ ] 公网普通用户访问资源 A 成功
- [ ] 公网普通用户访问资源 B 返回 403
- [ ] 公网 admin 访问资源 B 成功
- [ ] REPORT.md 填写真实公网 URL

当前阶段未真实公网部署，公网 URL 留待部署完成后填写。

## 9. 文档验收

- [ ] README.md 包含本地运行说明
- [ ] README.md 包含 Docker 说明
- [ ] README.md 包含 Render / Railway 部署说明
- [ ] README.md 包含 LLM 配置说明
- [ ] README.md 包含测试账号
- [ ] REPORT.md 回答题目 5 个问题
- [ ] REPORT.md 包含 LLM 调试 / 优化心得
- [ ] docs/deployment.md 存在
- [ ] docs/final_checklist.md 存在

## 10. 最终交付材料

- [ ] GitHub 仓库链接
- [ ] 公网 URL
- [ ] 资源 B 测试账号
- [ ] README.md
- [ ] REPORT.md
- [ ] Dockerfile
- [ ] docs/deployment.md
- [ ] docs/final_checklist.md
