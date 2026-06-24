# Submission Summary

## 1. Project Repository

GitHub 仓库链接：待填写

## 2. Public URL

公网访问地址：待实际云平台部署完成后填写

## 3. Resource B Test Account

email: admin@example.com
password: Admin123456

## 4. What Was Implemented

- 注册 / 登录
- JWT 认证
- 资源 A/B 授权
- admin 测试账号
- LLM / mock 用户名审核
- 浏览器页面
- API 文档
- Dockerfile
- 部署说明
- smoke test

## 5. How to Verify Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
python scripts/smoke_test.py
```

## 6. How to Verify with Docker

```bash
docker build -t auth-llm-demo .
docker run --rm -p 8000:8000 --env-file .env auth-llm-demo
```

## 7. Documentation

- README.md
- REPORT.md
- docs/deployment.md
- docs/final_checklist.md

## 8. Notes

- 当前未真实公网部署时，Public URL 待填写。
- 不应提交 .env 或真实 API Key。
- 没有 OPENAI_API_KEY 时自动使用 mock checker。

## 9. LLM Provider Notes

- LLM provider support includes OpenAI-compatible / DeepSeek / mock fallback.
- DeepSeek uses `LLM_PROVIDER=deepseek`, `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, and `DEEPSEEK_BASE_URL`.
- No real API key should be committed. Without a real key, the Demo uses mock checker automatically.
