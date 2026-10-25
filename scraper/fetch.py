"""
fetch.py — 合规的网络访问层
- 强制 IPv4（避免沙箱 IPv6 直连失败）
- 可识别 UA + 联系邮箱
- robots.txt 解析（命中禁止路径即跳过）
- is_live(url)：官方链接存活检查
- 处理 EdUHK 等旧服务器的 legacy renegotiation SSL 问题
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import socket
import ssl
import time
import random
import urllib.error
import urllib.parse
import urllib.request
from urllib.robotparser import RobotFileParser

import config

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT：兼容 EdUHK 等旧服务器
_ssl_ctx.set_ciphers("DEFAULT@SECLEVEL=1")


class IPv4HTTPSHandler(urllib.request.HTTPSHandler):
    """强制 IPv4 连接、并携带兼容旧服务器 SSL 上下文的 HTTPS handler。"""

    def __init__(self, *args, **kwargs):
        kwargs["context"] = _ssl_ctx
        super().__init__(*args, **kwargs)

    def create_connection(self, *args, **kwargs):  # pragma: no cover
        kwargs["family"] = socket.AF_INET
        return super().create_connection(*args, **kwargs)


_opener = urllib.request.build_opener(IPv4HTTPSHandler())


def _session():
    return _opener


def _headers():
    return {
        "User-Agent": config.USER_AGENT,
        "Accept-Language": "en-HK,en;q=0.8,zh-HK;q=0.6,zh;q=0.4",
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
    }


def fetch_url(url: str, timeout: int | None = None, binary: bool = False):
    """合规抓取：返回 (status, content)。失败时 status 为 None。"""
    timeout = timeout or config.REQUEST_TIMEOUT
    req = urllib.request.Request(url, headers=_headers())
    try:
        with _session().open(req, timeout=timeout) as r:
            data = r.read()
            if not binary:
                data = data.decode("utf-8", "replace")
            return r.status, data
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # 网络/DNS/SSL 等
        return None, f"{type(e).__name__}: {e}"


def robots_allowed(url: str) -> bool:
    """检查 robots.txt 是否允许本 UA 访问该路径。无法获取时默认允许（透明 UA）。"""
    try:
        parsed = urllib.parse.urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(config.USER_AGENT, url)
    except Exception:
        return True


def is_live(url: str) -> tuple[bool, str]:
    """
    官方链接存活检查。返回 (是否存活, 说明)。
    用 HEAD/GET 探测，2xx 视为存活；4xx/5xx/超时视为失效。
    """
    req = urllib.request.Request(url, headers=_headers(), method="HEAD")
    try:
        with _session().open(req, timeout=config.REQUEST_TIMEOUT) as r:
            if 200 <= r.status < 400:
                return True, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        # 部分服务器不支持 HEAD，回退 GET 取前若干字节
        if e.code in (403, 405, 501):
            try:
                req2 = urllib.request.Request(url, headers=_headers())
                with _session().open(req2, timeout=config.REQUEST_TIMEOUT) as r2:
                    if 200 <= r2.status < 400:
                        return True, f"GET HTTP {r2.status}"
                return False, f"HTTP {e.code}"
            except Exception as e2:
                return False, f"GET failed: {type(e2).__name__}"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, f"{type(e).__name__}"
    return False, "no-response"


def polite_sleep():
    """单站请求间随机间隔，降低服务器负载。"""
    time.sleep(random.uniform(config.MIN_INTERVAL, config.MAX_INTERVAL))


if __name__ == "__main__":
    s, c = fetch_url("https://eduhk.hk/en/current-openings")
    print("eduhk status:", s, "len:", len(c) if c else 0)
    print("is_live sample:", is_live("https://eduhk.hk/en/current-openings"))
