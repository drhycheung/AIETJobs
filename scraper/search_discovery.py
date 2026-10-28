"""
search_discovery.py — Discovery of employer and university recruitment pages through
the Tavily search API.

What this module does and does not do
-------------------------------------
It searches with queries written in the language Hong Kong recruiters use, and keeps
only results that point at a recruitment page or an individual vacancy. Everything
else is rejected and the reason is logged, so the rules can be corrected from
observed data rather than guesswork.

Measured behaviour that shaped these rules (28 Oct 2026, three test queries):
- Searching *inside* a commercial job board returns the board's own category pages
  ("machine-learning-fresh-graduate-jobs"), never an individual post. Those pages are
  therefore rejected: publishing them would present a category listing as a vacancy.
- Searching the open web does return individual vacancy pages and recruitment pages
  on employers' own sites. That is the material this module keeps.

Compliance: no job board is scraped, no verification challenge is bypassed, and the
link recorded for a lead is always the page that was found, unmodified.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import fetch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCOVERED_PATH = os.path.join(ROOT, "data", "discovered.json")

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# Leads older than this are dropped from the store; official recruitment pages are
# long-lived, so this only removes pages that have stopped being found at all.
LEAD_RETENTION_DAYS = 60
LEAD_STORE_LIMIT = 200


# ---------------------------------------------------------------------------
# URL classification
# ---------------------------------------------------------------------------
# Individual vacancy on a commercial board. Only these shapes are accepted; a board
# URL that does not match is a category or search page and is rejected.
_BOARD_POST_PATTERNS = [
    r"recruit\.com\.hk/jobseeker/jobdetail\.aspx\?joborder=",
    r"recruit\.com\.hk/job-detail/",
    r"jobsdb\.com/(?:[a-z]{2}/)?job/\d+",
    r"ctgoodjobs\.hk/(?:ajob|job)/\d+",
    r"cpjobs\.com/(?:.*/)?job/\d+",
]
_BOARD_POST_RE = [re.compile(p, re.I) for p in _BOARD_POST_PATTERNS]

# Paths that are never a recruitment page, whatever else the path contains.
# 'pathway' catches university course pages such as 'career-pathways'.
_HARD_JUNK = (
    "/news", "/article", "/epaper", "/blog", "/wiki", "/login", "/signin",
    "job_details.php", "pathway", "/event", "/press", "jobsearch",
)
# Paths that indicate a programme or course rather than a recruitment page. These
# reject a URL only when no recruitment signal is present, because a real vacancy
# slug may contain words such as 'graduate-programme'.
_SOFT_JUNK = ("programme", "/program", "/admission", "/course", "/seminar", "/webinar")
# Paths that do indicate a recruitment page on an employer's own site.
_CAREER_WORDS = (
    "career", "job", "vacanc", "recruit", "hiring", "opening", "position",
    "apply", "join-us", "join_us", "work-with-us", "work_with_us",
)
# An individual vacancy usually carries an identifier segment, as in
# careers.example.com/vacancies/839/software-engineering-graduate-programme
_INDIVIDUAL_POST = re.compile(
    r"/(?:vacanc(?:y|ies)?|jobs?|careers?|positions?|openings?)/\d", re.I)


def _host(url: str) -> str:
    return (urllib.parse.urlparse(url).netloc or "").lower()


def _path(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return (parsed.path + "?" + parsed.query).lower()


def _is_board(host: str) -> bool:
    return any(d in host for d in config.COMMERCIAL_BOARDS)


def _is_approved_employer(host: str) -> bool:
    """Employer pages are approved by domain: automatically for Hong Kong
    universities and government sites, explicitly for the reviewed employer list."""
    if host.endswith(".edu.hk") or host.endswith(".gov.hk"):
        return True
    return any(host == d or host.endswith("." + d) for d in config.EMPLOYER_DOMAINS)


def classify_url(url: str) -> tuple[str, str]:
    """Return (kind, reason). kind is 'job_post', 'careers_page' or 'rejected'.

    A rejected result is never published; the reason is kept for the report so the
    approved domains and the URL rules can be corrected from real data.
    """
    if not url or not url.lower().startswith("http"):
        return "rejected", "not an http(s) URL"
    host = _host(url)
    if any(d in host for d in config.EXCLUDED_DOMAINS):
        return "rejected", f"excluded domain ({host})"

    if _is_board(host):
        # Boards are kept only for individual vacancies, never for their own
        # category or search pages.
        if any(p.search(url) for p in _BOARD_POST_RE):
            return "job_post", "individual vacancy on a job board"
        return "rejected", "job-board category or search page, not an individual vacancy"

    if not _is_approved_employer(host):
        return "rejected", f"employer domain not approved yet ({host})"

    path = _path(url)
    for junk in _HARD_JUNK:
        if junk in path:
            return "rejected", f"not a recruitment page (path contains '{junk}')"
    has_career_signal = any(w in path for w in _CAREER_WORDS)
    if has_career_signal and _INDIVIDUAL_POST.search(path):
        return "job_post", "individual vacancy on the employer's own site"
    if has_career_signal:
        return "careers_page", "employer recruitment page"
    for junk in _SOFT_JUNK:
        if junk in path:
            return "rejected", f"not a recruitment page (path contains '{junk}')"
    return "rejected", "no recruitment signal in the URL path"


# ---------------------------------------------------------------------------
# Tavily search
# ---------------------------------------------------------------------------
def tavily_search(query: str, max_results: int | None = None) -> tuple[list[dict], str]:
    """Run one query. Returns (results, note). The note records why a query failed,
    so a failure is visible in the daily report instead of reducing coverage silently."""
    if not TAVILY_API_KEY:
        return [], "TAVILY_API_KEY not set"
    payload = {
        "query": query,
        "max_results": max_results or config.TAVILY_MAX_RESULTS,
        "search_depth": "basic",
    }
    status, obj = fetch.post_json(
        config.TAVILY_ENDPOINT, payload,
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"})
    if status != 200 or not isinstance(obj, dict):
        return [], f"search API returned HTTP {status}"
    return obj.get("results", []) or [], "ok"


def discover_via_tavily() -> list[dict]:
    """Run every configured query once and return classified leads."""
    queries = config.DISCOVERY_QUERIES[: config.TAVILY_DAILY_QUERY_LIMIT]
    leads: list[dict] = []
    rejected = 0
    failures: list[str] = []
    for query in queries:
        results, note = tavily_search(query)
        if note != "ok":
            failures.append(note)
            continue
        for r in results:
            url = (r.get("url") or "").strip()
            kind, why = classify_url(url)
            if kind == "rejected":
                rejected += 1
                continue
            leads.append({
                "title": (r.get("title") or "").strip(),
                "employer": "",
                "official_link": url,
                "kind": kind,
                "discover_source": "Tavily search",
                "query": query,
                "classify_note": why,
                "snippet": (r.get("content") or "").strip()[:400],
            })
        fetch.polite_sleep()
    print(f"[discovery] {len(queries)} queries, {len(leads)} usable results, "
          f"{rejected} rejected (category pages / non-recruitment pages)")
    for f in sorted(set(failures)):
        print(f"[discovery] query failure: {f}")
    return leads


# ---------------------------------------------------------------------------
# Lead store: keeps a dated record of everything found, for audit and deduplication
# ---------------------------------------------------------------------------
def _load_store() -> list[dict]:
    if not os.path.exists(DISCOVERED_PATH):
        return []
    try:
        with open(DISCOVERED_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get("leads", [])
    except Exception as e:
        print(f"[discovery] could not read {DISCOVERED_PATH}: {e}")
        return []


def _save_store(leads: list[dict]) -> None:
    os.makedirs(os.path.dirname(DISCOVERED_PATH), exist_ok=True)
    payload = {
        "updated_at": datetime.date.today().isoformat(),
        "note": ("Leads found by the Tavily search API. Each entry records the day it "
                 "was first and last seen; rejected results are not stored."),
        "leads": leads,
    }
    with open(DISCOVERED_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _reclassify(leads: list[dict]) -> list[dict]:
    """Apply the current classification rules to stored leads, so that a rule change
    also cleans up entries recorded before it. Rejected leads are dropped."""
    kept: list[dict] = []
    for lead in leads:
        kind, why = classify_url(lead.get("official_link", ""))
        if kind == "rejected":
            continue
        lead["kind"] = kind
        lead["classify_note"] = why
        kept.append(lead)
    return kept


def merge_leads(found: list[dict]) -> list[dict]:
    """Merge today's findings into the store and return the store.

    A page that is still found keeps its first_seen date; one that is no longer
    found stays in the store until it has not been seen for LEAD_RETENTION_DAYS.
    """
    today = datetime.date.today().isoformat()
    store = {l.get("official_link"): l
             for l in _reclassify(_load_store()) if l.get("official_link")}
    for lead in found:
        key = lead["official_link"]
        if key in store:
            store[key].update({
                "title": lead.get("title") or store[key].get("title", ""),
                "kind": lead.get("kind") or store[key].get("kind"),
                "last_seen": today,
                "query": lead.get("query") or store[key].get("query"),
                "snippet": lead.get("snippet") or store[key].get("snippet", ""),
            })
        else:
            lead["first_seen"] = today
            lead["last_seen"] = today
            store[key] = lead

    cutoff = (datetime.date.today()
              - datetime.timedelta(days=LEAD_RETENTION_DAYS)).isoformat()
    kept = [l for l in store.values() if (l.get("last_seen") or today) >= cutoff]
    kept.sort(key=lambda l: (l.get("last_seen") or "", l.get("official_link") or ""),
              reverse=True)
    kept = kept[:LEAD_STORE_LIMIT]
    _save_store(kept)
    return kept


# ---------------------------------------------------------------------------
# Lead -> unified job dictionary
# ---------------------------------------------------------------------------
def _official_type(kind: str, url: str) -> str:
    if _is_board(_host(url)):
        return "commercial_board"
    return "employer_vacancy" if kind == "job_post" else "employer_careers_page"


def convert_lead_to_job(lead: dict) -> dict:
    """Convert one lead into the unified job dictionary."""
    kind = lead.get("kind") or "careers_page"
    return {
        "title": (lead.get("title") or "").strip(),
        "employer": (lead.get("employer") or "").strip() or _host(lead.get("official_link", "")),
        "department": lead.get("department") or "",
        "location": lead.get("location") or "Hong Kong",
        "degree": lead.get("degree") or "Bachelor (fresh graduate welcome)",
        "experience": lead.get("experience") or "Not specified / entry-level",
        "description": lead.get("snippet") or lead.get("description") or "",
        "posted_date": lead.get("posted_date"),
        "deadline": lead.get("deadline"),
        "discover_source": lead.get("discover_source") or "Tavily search",
        "discovered_on": lead.get("first_seen") or "",
        "official_link": lead.get("official_link", ""),
        "official_type": _official_type(kind, lead.get("official_link", "")),
        "status": "active",
    }


def discover() -> list[dict]:
    """Return the leads to publish. With an API key the search runs and the store is
    updated; without one the store is used unchanged (nothing is fabricated)."""
    if TAVILY_API_KEY and config.EMPLOYER_DISCOVERY_ENABLED:
        found = discover_via_tavily()
        return merge_leads(found)
    print("[discovery] TAVILY_API_KEY not set; using the stored leads unchanged")
    return _reclassify(_load_store())


def collect_leads_as_jobs() -> list[dict]:
    """Discovery entry point used by the pipeline."""
    if not config.EMPLOYER_DISCOVERY_ENABLED:
        return []
    leads = discover()
    jobs = [convert_lead_to_job(l) for l in leads if l.get("official_link")]
    print(f"[discovery] {len(jobs)} leads to verify "
          f"(employer recruitment pages and individual vacancies)")
    return jobs


if __name__ == "__main__":
    for job in collect_leads_as_jobs():
        print(f"[{job['official_type']}] {job['title'][:70]} | {job['official_link']}")
