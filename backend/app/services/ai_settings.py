"""AI 服务配置的读写与缓存。

优先级：数据库 system_settings > .env/默认值（settings）。
自部署场景下，用户可在登录前通过配置向导填写自己的 API-KEY 与 Base URL，
保存后立即生效，无需修改 .env 或重启服务。
"""
import json
import logging
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.system import SystemSetting, UserAISetting

logger = logging.getLogger("ai_settings")

# 数据库中的配置键
KEY_MODE = "ai_mode"
KEY_BASE_URL = "llm_base_url"
KEY_API_KEY = "llm_api_key"
KEY_MODEL = "llm_model"

# 进程内缓存：配置读取远多于写入，保存时主动失效
_cache: Optional[dict] = None


def mask_key(api_key: str) -> str:
    """脱敏展示 API Key，仅保留头尾少量字符。"""
    if not api_key:
        return ""
    if len(api_key) <= 8:
        return "•" * len(api_key)
    return api_key[:3] + "•" * 8 + api_key[-4:]


def get_effective_config(db: Optional[Session] = None) -> dict:
    """返回当前生效的 AI 配置（DB 覆盖 .env 默认值），带进程内缓存。"""
    global _cache
    if _cache is not None:
        return dict(_cache)

    overrides = {}
    if db is not None:
        rows = db.query(SystemSetting).filter(
            SystemSetting.key.in_([KEY_MODE, KEY_BASE_URL, KEY_API_KEY, KEY_MODEL])
        ).all()
        overrides = {r.key: (r.value or "") for r in rows}

    config = {
        "mode": (overrides.get(KEY_MODE) or settings.AI_MODE or "real").strip().lower(),
        "base_url": overrides.get(KEY_BASE_URL) or settings.LLM_BASE_URL,
        "api_key": overrides.get(KEY_API_KEY) or settings.LLM_API_KEY,
        "model": overrides.get(KEY_MODEL) or settings.LLM_MODEL,
        "configured": bool(overrides.get(KEY_API_KEY) or settings.LLM_API_KEY),
    }
    _cache = dict(config)
    return config


def invalidate_cache() -> None:
    """失效全局配置缓存（用户级配置派生自全局配置，需一并失效）。"""
    global _cache
    _cache = None
    _user_cache.clear()


def save_config(db: Session, data: dict) -> dict:
    """保存配置（仅更新提交的字段；api_key 传空字符串表示保持不变）。"""
    mapping = {
        "mode": (KEY_MODE, lambda v: str(v).strip().lower()),
        "base_url": (KEY_BASE_URL, lambda v: str(v).strip().rstrip("/")),
        "api_key": (KEY_API_KEY, lambda v: str(v).strip()),
        "model": (KEY_MODEL, lambda v: str(v).strip()),
    }
    for field, (key, normalizer) in mapping.items():
        if field not in data or data[field] is None:
            continue
        value = normalizer(data[field])
        if field == "api_key" and value == "":
            continue  # 空 Key 视为"不修改"
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(SystemSetting(key=key, value=value))
    db.commit()
    invalidate_cache()
    return get_effective_config(db)


# 用户级配置进程内缓存：{user_id: config}
_user_cache: dict = {}


def get_user_effective_config(db: Optional[Session], user_id: Optional[int]) -> dict:
    """返回某用户生效的 AI 配置：用户级字段覆盖全局配置，缺省字段回退全局。

    user_id 为空（未登录/后台任务）时等价于全局配置。
    """
    if not user_id:
        return get_effective_config(db)

    if user_id in _user_cache:
        return dict(_user_cache[user_id])

    base = get_effective_config(db)
    row = db.query(UserAISetting).filter(UserAISetting.user_id == user_id).first() if db is not None else None
    if row is None:
        return base

    config = dict(base)
    if row.mode:
        config["mode"] = row.mode.strip().lower()
    if row.base_url:
        config["base_url"] = row.base_url
    if row.api_key:
        config["api_key"] = row.api_key
        config["configured"] = True
    if row.model:
        config["model"] = row.model
    _user_cache[user_id] = dict(config)
    return config


def save_user_config(db: Session, user_id: int, data: dict) -> dict:
    """保存用户级 AI 配置（仅更新提交字段；api_key 传空字符串表示保持不变）。"""
    row = db.query(UserAISetting).filter(UserAISetting.user_id == user_id).first()
    if row is None:
        row = UserAISetting(user_id=user_id)
        db.add(row)
    if "mode" in data and data["mode"] is not None:
        row.mode = str(data["mode"]).strip().lower()
    if "base_url" in data and data["base_url"] is not None:
        row.base_url = str(data["base_url"]).strip().rstrip("/") or None
    if "model" in data and data["model"] is not None:
        row.model = str(data["model"]).strip() or None
    if "api_key" in data and str(data["api_key"]).strip() != "":
        row.api_key = str(data["api_key"]).strip()
    db.commit()
    _user_cache.pop(user_id, None)
    return get_user_effective_config(db, user_id)


def reset_user_config(db: Session, user_id: int) -> None:
    """清除用户级配置，回退到全局配置。"""
    row = db.query(UserAISetting).filter(UserAISetting.user_id == user_id).first()
    if row:
        db.delete(row)
        db.commit()
    _user_cache.pop(user_id, None)


def invalidate_user_cache(user_id: Optional[int] = None) -> None:
    if user_id is None:
        _user_cache.clear()
    else:
        _user_cache.pop(user_id, None)


def validate_base_url(base_url: str) -> Optional[str]:
    """校验 Base URL 仅允许 http/https 协议，返回错误信息或 None。"""
    if not base_url:
        return "Base URL 不能为空"
    if not base_url.startswith(("http://", "https://")):
        return "Base URL 必须以 http:// 或 https:// 开头"
    return None


async def test_connection(base_url: str, api_key: str, model: str) -> dict:
    """向目标端点发送一条最小 chat 请求验证配置有效性。"""
    err = validate_base_url(base_url)
    if err:
        return {"success": False, "message": err}
    if not api_key:
        return {"success": False, "message": "API Key 不能为空"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or "gpt-4o-mini",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                return {"success": True, "message": "连接成功，API Key 与模型可用"}
            return {"success": False, "message": f"服务返回 HTTP {res.status_code}，请检查模型、地址与授权配置"}
    except httpx.TimeoutException:
        return {"success": False, "message": "连接超时（15 秒），请检查 Base URL 与网络"}
    except Exception:
        return {"success": False, "message": "连接失败，请检查服务地址与网络"}
