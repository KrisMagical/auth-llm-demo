"""Username moderation via OpenAI-compatible LLM with mock fallback."""

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

RISKY_KEYWORDS = (
    "fuck",
    "shit",
    "scam",
    "fraud",
    "phishing",
    "official",
    "admin",
    "root",
    "hate",
    "terrorist",
)

VALID_LLM_STATUSES = {"allowed", "rejected", "uncertain"}


def mock_check_username(username: str) -> dict[str, str]:
    """Check a username with deterministic local rules."""
    normalized_username = username.lower()
    if any(keyword in normalized_username for keyword in RISKY_KEYWORDS):
        return {
            "status": "mock_rejected",
            "reason": "Mock checker detected risky keyword.",
            "provider": "mock",
        }

    return {
        "status": "mock_allowed",
        "reason": "Mock checker passed.",
        "provider": "mock",
    }


def strip_json_code_fence(content: str) -> str:
    """Remove a Markdown JSON code fence when the LLM returns one."""
    stripped_content = content.strip()
    fenced_match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        stripped_content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if fenced_match:
        return fenced_match.group(1).strip()
    return stripped_content


def parse_llm_response(content: str) -> dict[str, str]:
    """Parse and normalize an LLM moderation response."""
    try:
        parsed: dict[str, Any] = json.loads(strip_json_code_fence(content))
    except json.JSONDecodeError:
        return {
            "status": "failed",
            "reason": "LLM returned invalid JSON.",
            "provider": "openai",
        }

    status = parsed.get("status")
    if status not in VALID_LLM_STATUSES:
        return {
            "status": "failed",
            "reason": "LLM returned invalid status.",
            "provider": "openai",
        }

    reason = parsed.get("reason") or "LLM username check completed."
    return {
        "status": status,
        "reason": str(reason),
        "provider": "openai",
    }


def check_username(username: str) -> dict[str, str]:
    """Check whether a username should be allowed during registration."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not openai_api_key or llm_provider != "openai":
        return mock_check_username(username)

    prompt = f"""
你是一个社区注册用户名审核器。

请判断下面的 username 是否存在社区违规风险。

重点关注：
1. 辱骂、仇恨、歧视
2. 色情、暴力、违法
3. 诈骗、钓鱼、冒充官方
4. 明显恶意或攻击性表达

username: {username}

请只返回 JSON，不要返回 Markdown，不要解释多余内容。

返回格式：
{{
  "status": "allowed" | "rejected" | "uncertain",
  "reason": "简短原因"
}}
""".strip()

    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model=openai_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict but not overly sensitive community "
                        "username moderation assistant."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return parse_llm_response(content)
    except Exception:
        return {
            "status": "failed",
            "reason": "LLM username check failed.",
            "provider": "openai",
        }
