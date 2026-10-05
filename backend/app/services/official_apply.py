import ipaddress
from urllib.parse import urlsplit


def validate_official_url(value):
    """只保存可在浏览器打开的 HTTPS 招聘页；不在服务端抓取链接。"""
    if value is None or not str(value).strip():
        return None
    value = str(value).strip()
    try:
        url = urlsplit(value)
        host = url.hostname or ""
        if url.scheme != "https" or not host or url.username or url.password:
            raise ValueError()
        if url.port not in (None, 443) or "." not in host or host.endswith(".local"):
            raise ValueError()
        if host.lower() == "localhost" or any(c in value for c in "\\\r\n\t") or len(value) > 2048:
            raise ValueError()
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("请填写企业官网或授权招聘系统的 HTTPS 链接，不能使用本地地址或带账号密码的链接")
    return value
