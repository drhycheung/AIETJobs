"""
fetch.py — Compliant network access layer
- Force IPv4 (avoids sandbox IPv6 direct-connection failures)
- Identifiable UA + contact email
- robots.txt parsing (skip when a forbidden path is matched)
- is_live(url): official link liveness check
- Handles legacy renegotiation SSL issues on legacy servers such as EdUHK
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
_ssl_ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT: compatible with legacy servers such as EdUHK
_ssl_ctx.set_ciphers("DEFAULT@SECLEVEL=1")


class IPv4HTTPSHandler(urllib.request.HTTPSHandler):
    """HTTPS handler that forces IPv4 connections and carries an SSL context
    compatible with legacy servers."""

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
    """Compliant fetch: returns (status, content). On failure, status is None."""
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
    except Exception as e:  # network / DNS / SSL etc.
        return None, f"{type(e).__name__}: {e}"


def robots_allowed(url: str) -> bool:
    """Check whether robots.txt allows this UA to access the path.
    Defaults to allowed when robots.txt cannot be fetched (transparent UA)."""
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
    Official link liveness check. Returns (is_alive, explanation).
    Probes with HEAD/GET; 2xx counts as alive; 4xx/5xx/timeout counts as dead.
    """
    req = urllib.request.Request(url, headers=_headers(), method="HEAD")
    try:
        with _session().open(req, timeout=config.REQUEST_TIMEOUT) as r:
            if 200 <= r.status < 400:
                return True, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        # Some servers do not support HEAD; fall back to GET and read the first bytes
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
    """Random interval between requests to a single site, to reduce server load."""
    time.sleep(random.uniform(config.MIN_INTERVAL, config.MAX_INTERVAL))


if __name__ == "__main__":
    s, c = fetch_url("https://eduhk.hk/en/current-openings")
    print("eduhk status:", s, "len:", len(c) if c else 0)
    print("is_live sample:", is_live("https://eduhk.hk/en/current-openings"))
