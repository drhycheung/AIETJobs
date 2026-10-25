"""
search_discovery.py — Discovery module for commercial job boards (compliant: links only,
no direct scraping, no bypass of verification)

Compliance design (see AGENTS.md sections 1.3 / 2):
- Major Hong Kong job boards (JobsDB / CTgoodjobs / Recruit / CPjobs) are discovered
  through public search-engine indexing; we never script-scrape the boards and never
  bypass any human-verification challenge.
- Discovered links serve only as "job-board post" leads and must pass is_live before
  inclusion; because board deep links are short-lived (about 30 days), they are
  re-discovered daily and the source is labelled honestly.

Two discovery backends:
1. A search API configured (Google Programmable Search / Bing / SerpAPI) -> automatically
   searches the five-direction keywords.
2. No API configured -> read data/discovered.json (real posts found by the agent via
   WebSearch, recorded manually here, never fabricated). In neither case is fake data produced.
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

# Search API configuration (env vars or config); falls back to the local leads file if unset
SEARCH_API = os.environ.get("AIET_SEARCH_API", "")
SEARCH_API_KEY = os.environ.get("AIET_SEARCH_KEY", "")


def discover_queries() -> list[str]:
    """Generate search queries for the five directions (common Chinese / English /
    Cantonese phrasings)."""
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
# Candidate post -> unified job dictionary
# ---------------------------------------------------------------------------
def convert_lead_to_job(lead: dict) -> dict:
    """Convert one discovered candidate post (from a search API or local leads) into
    the unified job dictionary."""
    domain = (urllib.parse.urlparse(lead.get("official_link", "")).netloc or "").lower()
    board_name = "Commercial job board"
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
        "discover_source": f"{board_name} (job-board discovery)",
        "official_link": lead.get("official_link", ""),
        "official_type": "commercial_board",
        "status": "active",
    }


# ---------------------------------------------------------------------------
# Local leads (used when no search API is configured; real posts recorded by the
# agent via WebSearch)
# ---------------------------------------------------------------------------
def load_local_leads() -> list[dict]:
    if not os.path.exists(DISCOVERED_PATH):
        return []
    try:
        with open(DISCOVERED_PATH, encoding="utf-8") as f:
            data = json.load(f)
        leads = data if isinstance(data, list) else data.get("leads", [])
        # Keep only links that are whitelisted and not in an excluded domain
        kept = [l for l in leads if whitelisted(l.get("official_link", ""))
                and not excluded(l.get("official_link", ""))]
        print(f"[discovery] read local leads {len(kept)}/{len(leads)} (filtered non-whitelist / excluded domains)")
        return kept
    except Exception as e:
        print(f"[discovery] failed to read {DISCOVERED_PATH}: {e}")
        return []


# ---------------------------------------------------------------------------
# Search API backend (enabled once configured; keep low-frequency, identifiable UA,
# and comply with Terms of Service)
# ---------------------------------------------------------------------------
def _search_via_api() -> list[dict]:
    """Call the configured search API and return a list of candidate posts
    (with title / employer / official_link)."""
    import fetch  # reuse forced IPv4 + identifiable UA
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
    # google / others: extend here (stay compliant). Falls back to local leads if unimplemented.
    return leads


# ---------------------------------------------------------------------------
# Main entry: return candidate posts (filtered by whitelist / excluded domains)
# ---------------------------------------------------------------------------
def discover() -> list[dict]:
    if SEARCH_API and SEARCH_API_KEY:
        leads = _search_via_api()
        if leads:
            return leads
        print("[discovery] search API returned no results; falling back to local leads")
    return load_local_leads()


def collect_leads_as_jobs() -> list[dict]:
    """Discover candidate posts and convert to job dictionaries (returns empty, no
    fabrication, when no API is configured and no local leads exist)."""
    if not config.COMMERCIAL_DISCOVERY_ENABLED:
        return []
    leads = discover()
    jobs = [convert_lead_to_job(l) for l in leads if l.get("official_link")]
    print(f"[discovery] commercial job boards discovered {len(jobs)} candidates ({', '.join(config.COMMERCIAL_BOARDS.values())})")
    return jobs


# ---------------------------------------------------------------------------
# Link whitelist / excluded-domain checks
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
