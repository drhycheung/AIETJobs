"""
search_discovery.py — 商业求职板「发现」模块（合规：仅取链接，不直爬、不绕验证）

合规设计（AGENTS.md §1.3 / §2）：
- 香港主流求职网站（JobsDB / CTgoodjobs / Recruit / CPjobs）经**搜索引擎公开索引**
  发现帖子 URL，绝不写脚本直爬求职板、绝不绕过任何人机验证。
- 发现的链接仅作「求职板原帖」线索，最终收录前必须 is_live 存活校验；
  商业板深链有效期短（约 30 天），故每日重新发现，并如实标注来源。

两种发现后端：
1. 配置了搜索 API（Google Programmable Search / Bing / SerpAPI）→ 自动检索五类关键词。
2. 未配置 API → 读取 data/discovered.json（由智能体经 WebSearch 发现的真实帖子，
   人工落地为本文件，绝不编造）。两种情况下都不会产出伪造数据。
"""
from __future__ import annotations

import os
import sys
import json
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCOVERED_PATH = os.path.join(ROOT, "data", "discovered.json")

# 搜索 API 配置（环境变量或 config 中填写）；未配置则回退到本地 leads 文件
SEARCH_API = os.environ.get("AIET_SEARCH_API", "")
SEARCH_API_KEY = os.environ.get("AIET_SEARCH_KEY", "")


def discover_queries() -> list[str]:
    """生成五类方向的检索式（中/英/粤语常见写法）。"""
    return [
        "AI graduate trainee Hong Kong",
        "machine learning data analyst fresh graduate Hong Kong",
        "EdTech developer Hong Kong",
        "AI 教學助理 香港",
        "數據標註 香港 實習",
        "STEM instructor Hong Kong",
        "research assistant artificial intelligence Hong Kong",
        "IT programmer fresh graduate Hong Kong",
        "data science trainee Hong Kong",
    ]


# ---------------------------------------------------------------------------
# 候选帖子 → 统一岗位字典
# ---------------------------------------------------------------------------
def convert_lead_to_job(lead: dict) -> dict:
    """将一条发现的候选帖子（来自搜索 API 或本地 leads）转为统一岗位字典。"""
    domain = (urllib.parse.urlparse(lead.get("official_link", "")).netloc or "").lower()
    board_name = "商业求职板"
    for d, name in config.COMMERCIAL_BOARDS.items():
        if d in domain:
            board_name = name
            break
    return {
        "title": lead.get("title", "").strip(),
        "employer": lead.get("employer", "").strip() or board_name,
        "department": lead.get("department", "") or "",
        "location": lead.get("location", "") or "Hong Kong",
        "degree": lead.get("degree", "") or "Bachelor (fresh graduate welcome)",
        "experience": lead.get("experience", "") or "Not specified / entry-level",
        "description": lead.get("description", "") or "",
        "posted_date": lead.get("posted_date"),
        "deadline": lead.get("deadline"),
        "discover_source": f"{board_name}（求职板发现）",
        "official_link": lead.get("official_link", ""),
        "official_type": "commercial_board",
        "status": "active",
    }


# ---------------------------------------------------------------------------
# 本地 leads（未配置搜索 API 时使用，由智能体经 WebSearch 落地真实帖子）
# ---------------------------------------------------------------------------
def load_local_leads() -> list[dict]:
    if not os.path.exists(DISCOVERED_PATH):
        return []
    try:
        with open(DISCOVERED_PATH, encoding="utf-8") as f:
            data = json.load(f)
        leads = data if isinstance(data, list) else data.get("leads", [])
        # 仅保留白名单内、未被排除域的链接
        kept = [l for l in leads if whitelisted(l.get("official_link", ""))
                and not excluded(l.get("official_link", ""))]
        print(f"[discovery] 读取本地 leads {len(kept)}/{len(leads)} 条（已过滤非白名单/排除域）")
        return kept
    except Exception as e:
        print(f"[discovery] 读取 {DISCOVERED_PATH} 失败：{e}")
        return []


# ---------------------------------------------------------------------------
# 搜索 API 后端（配置后启用；保持低频、可识别 UA、遵守 ToS）
# ---------------------------------------------------------------------------
def _search_via_api() -> list[dict]:
    """调用配置的搜索 API，返回候选帖子列表（含 title/employer/official_link）。"""
    import fetch  # 复用强制 IPv4 + 可识别 UA
    leads: list[dict] = []
    if SEARCH_API == "bing":
        # Bing Web Search v7
        for q in discover_queries():
            url = "https://api.bing.microsoft.com/v7.0/search?count=20&q=" + urllib.parse.quote(q)
            status, raw = fetch.fetch_url(url, headers={
                "Ocp-Apim-Subscription-Key": SEARCH_API_KEY,
                "User-Agent": config.USER_AGENT,
            })
            if status != 200 or not raw:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            for r in obj.get("webPages", {}).get("value", []):
                link = r.get("url", "")
                if not whitelisted(link) or excluded(link):
                    continue
                leads.append({
                    "title": r.get("name", ""),
                    "employer": "",
                    "official_link": link,
                })
            fetch.polite_sleep()
    elif SEARCH_API == "serpapi":
        for q in discover_queries():
            url = ("https://serpapi.com/search.json?engine=google&num=20&q="
                   + urllib.parse.quote(q) + "&api_key=" + SEARCH_API_KEY)
            status, raw = fetch.fetch_url(url, headers={"User-Agent": config.USER_AGENT})
            if status != 200 or not raw:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            for r in obj.get("organic_results", []):
                link = r.get("link", "")
                if not whitelisted(link) or excluded(link):
                    continue
                leads.append({
                    "title": r.get("title", ""),
                    "employer": "",
                    "official_link": link,
                })
            fetch.polite_sleep()
    # google / 其他：在此扩展（保持合规）。未实现则回退本地 leads。
    return leads


# ---------------------------------------------------------------------------
# 主入口：返回候选帖子（经白名单/排除域过滤）
# ---------------------------------------------------------------------------
def discover() -> list[dict]:
    if SEARCH_API and SEARCH_API_KEY:
        leads = _search_via_api()
        if leads:
            return leads
        print("[discovery] 搜索 API 无结果，回退本地 leads")
    return load_local_leads()


def collect_leads_as_jobs() -> list[dict]:
    """发现候选帖子并转为岗位字典（未配置 API 且本地无 leads 时返回空，不编造）。"""
    if not config.COMMERCIAL_DISCOVERY_ENABLED:
        return []
    leads = discover()
    jobs = [convert_lead_to_job(l) for l in leads if l.get("official_link")]
    print(f"[discovery] 商业求职板发现 {len(jobs)} 条候选（{', '.join(config.COMMERCIAL_BOARDS.values())}）")
    return jobs


# ---------------------------------------------------------------------------
# 链接白名单 / 排除域校验
# ---------------------------------------------------------------------------
def whitelisted(url: str) -> bool:
    host = (urllib.parse.urlparse(url).netloc or "").lower()
    return any(d in host for d in config.ALLOWED_DOMAINS)


def excluded(url: str) -> bool:
    host = (urllib.parse.urlparse(url).netloc or "").lower()
    return any(d in host for d in config.EXCLUDED_DOMAINS)


if __name__ == "__main__":
    for j in collect_leads_as_jobs():
        print(j["title"], "|", j["discover_source"], "|", j["official_link"])
