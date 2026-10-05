"""请求隔离的调用上下文；日志不记录简历、答案、密钥等原文。"""
from contextvars import ContextVar
from contextlib import contextmanager

PROMPT_VERSION = "v4.0"
RUBRIC_VERSION = "rubric-6d-v1"
call_context = ContextVar("ai_call_context", default={})
last_result = ContextVar("ai_last_result", default={})


@contextmanager
def ai_context(user_id=None, business_id=None, request_id=None):
    token = call_context.set({"user_id": user_id, "business_id": business_id, "request_id": request_id})
    result_token = last_result.set({})
    try:
        yield
    finally:
        last_result.reset(result_token)
        call_context.reset(token)


def metadata(source, model, fallback_reason=None):
    value = {"source": source, "model": model, "fallback_reason": fallback_reason,
             "prompt_version": PROMPT_VERSION, "rubric_version": RUBRIC_VERSION}
    last_result.set(value)
    return value


def traced(method):
    from functools import wraps
    @wraps(method)
    async def wrapper(*args, **kwargs):
        last_result.set({})
        result = await method(*args, **kwargs)
        if isinstance(result, dict):
            result["_ai_meta"] = dict(last_result.get()) or metadata("UNKNOWN", "unknown")
        return result
    return wrapper
