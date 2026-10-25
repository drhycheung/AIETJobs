"""
live.py — 白名单官方页直抓适配器
当前完整实现：香港教育大学 EdUHK（current-openings，官方 PDF 原帖）
其他大学：框架占位，待各自 ATS 接入后启用（保持空白而非编造数据）。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import html
import urllib.parse
from html.parser import HTMLParser

import config
import fetch
import search_discovery


# ---------------------------------------------------------------------------
# EdUHK 适配器
# ---------------------------------------------------------------------------
class _EduhkParser(HTMLParser):
    """解析 EdUHK current-openings 页：每个 .job__item 为一个岗位。"""

    def __init__(self):
        super().__init__()
        self.jobs: list[dict] = []
        self._in_item = False
        self._div_depth = 0
        self._in_title_a = False
        self._in_from = False
        self._in_dd = False
        self._cur_dt = None
        self._buf = []
        self._cur = None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class", "")
        if "job__item" in cls:
            self._in_item = True
            self._div_depth = 1
            self._cur = {"title": "", "href": "", "department": "",
                         "ref": "", "ad_date": "", "close_date": ""}
            return
        if not self._in_item:
            return
        if tag == "div":
            self._div_depth += 1
            return
        if tag == "a" and "job__title-name" in cls:
            self._in_title_a = True
            self._cur["href"] = d.get("href", "")
            return
        if tag == "p" and "job__title-from" in cls:
            self._in_from = True
            return
        if tag == "dt" and "job__dt" in cls:
            self._cur_dt = "pending"
            self._buf = []
            return
        if tag == "dd" and "job__dd" in cls:
            self._in_dd = True
            self._buf = []
            return

    def handle_endtag(self, tag):
        if not self._in_item:
            return
        if tag == "a" and self._in_title_a:
            self._in_title_a = False
            return
        if tag == "p" and self._in_from:
            self._in_from = False
            self._cur["department"] = html.unescape("".join(self._buf)).strip()
            self._buf = []
            return
        if tag == "dt":
            self._cur_dt = html.unescape("".join(self._buf)).strip().rstrip(":")
            self._buf = []
            return
        if tag == "dd" and self._in_dd:
            self._in_dd = False
            val = html.unescape("".join(self._buf)).strip()
            key = (self._cur_dt or "").lower()
            if "ref" in key:
                self._cur["ref"] = val
            elif "ad date" in key:
                self._cur["ad_date"] = val
            elif "close date" in key:
                self._cur["close_date"] = val
            self._buf = []
            return
        if tag == "div":
            self._div_depth -= 1
            if self._div_depth <= 0:
                self._commit()
            return

    def handle_data(self, data):
        if self._in_title_a and self._cur is not None:
            self._cur["title"] += data
        elif self._in_from or self._in_dd or self._cur_dt == "pending":
            self._buf.append(data)

    def _commit(self):
        if self._cur and self._cur.get("title"):
            self._cur["title"] = html.unescape(self._cur["title"]).strip()
            if self._cur["title"]:
                self.jobs.append(self._cur)
        self._cur = None
        self._in_item = False
        self._div_depth = 0


def collect_eduhk() -> list[dict]:
    """抓取并解析 EdUHK 当前空缺页（含分页），返回岗位字典列表（未经合规过滤）。"""
    base = "https://eduhk.hk/en/current-openings"
    if not fetch.robots_allowed(base):
        print(f"[eduhk] robots.txt 禁止访问 {base}，跳过")
        return []
    jobs: list[dict] = []
    seen_links = set()
    for page in range(1, 8):  # 最多 7 页，超出即停止
        url = base if page == 1 else f"{base}/page{page}"
        status, content = fetch.fetch_url(url)
        if status != 200 or not content or 'class="job__item"' not in content:
            break
        p = _EduhkParser()
        p.feed(content)
        if p._cur:
            p._commit()
        page_jobs = p.jobs
        if not page_jobs:
            break
        for j in page_jobs:
            if j["href"] in seen_links:
                continue
            seen_links.add(j["href"])
            jobs.append(j)
        if len(page_jobs) < 10:
            break
        fetch.polite_sleep()
    # 转换为统一岗位字典
    out = []
    for j in jobs:
        href = j["href"]
        if href.startswith("/"):
            href = urllib.parse.urljoin("https://eduhk.hk", href)
        out.append({
            "title": j["title"],
            "employer": "The Education University of Hong Kong (EdUHK)",
            "department": j["department"],
            "location": "Hong Kong",
            "degree": "Bachelor (fresh graduate welcome)",
            "experience": "Not specified / entry-level",
            "posted_date": j["ad_date"] or None,
            "deadline": j["close_date"] or None,
            "discover_source": "EdUHK official vacancies",
            "official_link": href,
            "official_type": "employer_official",
            "status": "active",
        })
    print(f"[eduhk] 解析到 {len(out)} 个岗位（含分页去重）")
    return out


# ---------------------------------------------------------------------------
# 其他大学框架（占位：返回空，避免编造；接入后按 EdUHK 模式扩展）
# ---------------------------------------------------------------------------
def collect_university(domain: str) -> list[dict]:
    """通用占位：当前未实现对应 ATS 解析，返回空列表。"""
    print(f"[live] {domain} 适配器尚未启用（框架占位，未编造数据）")
    return []


def collect_all() -> list[dict]:
    """汇总所有已启用的来源：大学官方页 + 商业求职板（经搜索发现）。"""
    jobs = collect_eduhk()
    # 商业求职板：经搜索引擎发现链接（不直爬、不绕验证）
    jobs += search_discovery.collect_leads_as_jobs()
    # 其他大学待接入：HKUST / CUHK / HKU / PolyU / CityU / HKBU / Lingnan / HKSYU
    return jobs


if __name__ == "__main__":
    for job in collect_all():
        print(job["title"], "|", job["department"], "|", job["deadline"], "|", job["official_link"])
