"""
pipeline.py — Deduplication / categorisation / star fit-score / compliance filter / sorting
Core principles (see AGENTS.md):
- Only collect posts that are "open to bachelor graduates / fresh graduate welcome".
- Programmatic filtering: requires experience / licence / Master's, already closed,
  dead link, non-Hong Kong, or not whitelisted.
- The final link must be the official post and must pass is_live verification.
"""
from __future__ import annotations

import os
import sys
import re
import io
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import fetch
from live import collect_all

try:
    from pypdf import PdfReader
    _HAVE_PYPDF = True
except Exception:
    _HAVE_PYPDF = False


# ---------------------------------------------------------------------------
# Categorisation
# ---------------------------------------------------------------------------
def _text_of(job: dict) -> str:
    return " ".join([
        job.get("title", ""), job.get("department", ""),
        job.get("employer", ""),
    ]).lower()


def assign_category(job: dict) -> tuple[int, int]:
    """Return (best category, keyword hit count for that category).
    A hit count of 0 means no match with the five directions."""
    text = _text_of(job)
    best, best_score = 3, 0  # Default to "Pure AI / ML" and differentiate by score
    for cat_id, meta in config.CATEGORIES.items():
        score = sum(1 for kw in meta["keywords"] if kw.lower() in text)
        if score > best_score:
            best, best_score = cat_id, score
    return best, best_score


# ---------------------------------------------------------------------------
# Star fit-score (BSc AI&EdTech competency profile)
# ---------------------------------------------------------------------------
_STRONG = {"ai", "artificial intelligence", "machine learning", "ml", "nlp",
           "education", "educational", "edtech", "learning", "teaching",
           "computer vision", "人工智能", "教育", "教学", "學習"}


def fit_score(job: dict, cat_score: int = 0) -> tuple[int, str]:
    text = _text_of(job)
    hits = []
    raw = 0
    for kw in config.FIT_KEYWORDS:
        if kw.lower() in text:
            hits.append(kw)
            raw += 2 if kw.lower() in _STRONG else 1
    cat = assign_category(job)[0]
    cat_name = config.CATEGORIES[cat]["name"]
    # Prefer university / same-field posts
    if "eduhk" in job.get("official_link", "") or "university" in job.get("employer", "").lower():
        raw += 1
    stars = 1 if raw >= 1 else 0
    stars = 2 if raw >= 4 else stars
    stars = 3 if raw >= 7 else stars
    stars = max(stars, 1)
    reason = "matched keywords: " + ", ".join(hits[:6]) if hits else "general AI/data post"
    return stars, f"Category = {cat_name}; {reason}"


# ---------------------------------------------------------------------------
# Compliance: extract text from the official PDF and check experience / degree
# ---------------------------------------------------------------------------
def _extract_pdf_text(url: str) -> str | None:
    if not _HAVE_PYPDF:
        return None
    status, data = fetch.fetch_url(url, binary=True)
    if status != 200 or not data:
        return None
    try:
        r = PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in r.pages)
    except Exception:
        return None


def _extract_html_text(url: str) -> str | None:
    """Commercial job-board deep links have no PDF, so fall back to scraping the
    page HTML to scan for experience / degree signals."""
    status, html_text = fetch.fetch_url(url)
    if status != 200 or not html_text:
        return None
    return html_text


def _get_jd_text(job: dict) -> str | None:
    """Fetch the JD text once: official posts use the PDF, job-board posts use
    page HTML (shared by compliance check and description extraction)."""
    if job.get("official_type") == "employer_official":
        return _extract_pdf_text(job.get("official_link", ""))
    return _extract_html_text(job.get("official_link", ""))


def _summarize(text: str, limit: int = 220) -> str:
    """Extract one short responsibility summary from the JD text
    (excluding header noise such as salary / reference numbers)."""
    if not text:
        return ""
    # Prefer a responsibilities paragraph
    paras = re.split(r"\n\s*\n|(?:\r\n)+", text)
    best = None
    for p in paras:
        pl = p.lower()
        if any(k in pl for k in ("duties", "responsibilities", "the appointee",
                                 "job description", "main responsibilities", "role")):
            if len(p.strip()) > 40:
                best = p
                break
    if not best:
        for p in paras:
            s = p.strip()
            if len(s) > 50 and not re.match(
                    r"(ref|closing date|advertisement|salary|the education university|"
                    r"job ref|post\s*ref|apply|enquiries)", s.lower()):
                best = p
                break
    if not best:
        best = re.sub(r"\s+", " ", text)
    s = re.sub(r"\s+", " ", best).strip()
    if len(s) > limit:
        s = s[:limit].rstrip() + "…"
    return s


def _build_description(job: dict, jd_text: str | None) -> str:
    """Job description: prefer the description attached at discovery time;
    otherwise summarise from the JD text."""
    if job.get("description"):
        return job["description"].strip()
    if jd_text:
        return _summarize(jd_text)
    return ""


def assign_tags(job: dict) -> list[str]:
    """Dynamically generate tags for the multi-tag display
    (direction tags + role / source tags)."""
    text = _text_of(job)
    tags: list[str] = []
    for label, kws in config.DIRECTION_TAGS.items():
        if any(k in text for k in kws):
            tags.append(label)
    title_l = job.get("title", "").lower()
    exp = (job.get("experience", "") or "").lower()
    employer = (job.get("employer", "") or "").lower()
    host = (urllib.parse.urlparse(job.get("official_link", "")).netloc or "").lower()
    is_university = ("university" in employer or "university" in title_l
                     or host.endswith(".edu.hk"))
    if is_university:
        tags.append("University")
    elif job.get("official_type") in ("commercial_board", "employer_vacancy",
                                      "employer_careers_page"):
        tags.append("Industry")
    if any(k in title_l for k in ("intern", "trainee", "part-time", "part time",
                                  "实习", "培训生", "培训生")):
        tags.append("Intern / Trainee")
    if any(k in exp for k in ("not required", "fresh graduate", "entry-level",
                              "welcome", "not specified")):
        tags.append("Fresh-graduate friendly")
    # Deduplicate while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def compliance_check(job: dict, jd_text: str | None = None) -> tuple[bool, str]:
    """Return (keep, explanation). jd_text may be pre-fetched by the caller
    to avoid downloading it twice."""
    title = job.get("title", "").lower()
    # 0) Academic / faculty titles (require a PhD; not for fresh bachelor graduates)
    for term in config.ACADEMIC_REJECT:
        if term in title:
            return False, f"Academic/faculty post (usually requires a PhD): '{term}'"
    # 1) Hard title rejection (seniority / management / experience required)
    for term in config.EXPERIENCE_REJECT:
        if term in title:
            return False, f"Title signals seniority / experience: '{term.strip()}'"
    # 2) Non-Hong Kong (based on title / department / employer)
    text = _text_of(job)
    for sig in config.NON_HK_SIGNALS:
        if sig in text:
            return False, f"Likely non-Hong Kong post: '{sig}'"
    # 3) Deep check of the official JD text (experience / degree): PDF first, then page HTML
    # An employer recruitment page lists whatever posts happen to be open, so there is
    # no single job description to check; the page states the requirements itself.
    if job.get("official_type") == "employer_careers_page":
        return True, ("Employer recruitment page; requirements are stated on the page "
                      "and change as individual posts open and close")
    scan = jd_text
    src = "PDF" if job.get("official_type") == "employer_official" else "page HTML"
    if scan is None:
        scan = _extract_pdf_text(job.get("official_link", ""))
        src = "PDF"
    if scan is None:
        scan = _extract_html_text(job.get("official_link", ""))
        src = "page HTML"
    if scan is None:
        return True, "(JD text not retrieved; students should verify requirements themselves)"
    pl = scan.lower()
    # A degree requirement counts as a rejection only when it is a hard requirement;
    # "a plus / preferred / advantage" does not count.
    _DEG_REQ = re.compile(
        r"(master'?s?|m\.?sc|m\.?phil|ph\.?d|doctorate|postgraduate).{0,45}?"
        r"(required|must|essential|minimum|necessar|qualif)", re.I)
    _DEG_REQ_ZH = re.compile(r"(硕士|博士).{0,12}(須|必须|要求|以上|學位)", re.I)
    _NEG = re.compile(r"\b(plus|advantage|preferred|asset|desirable|optional|nice to have|a plus)\b", re.I)
    for term in config.DEGREE_REJECT:
        if term not in pl:
            continue
        hit = _DEG_REQ.search(pl) or _DEG_REQ_ZH.search(pl)
        if hit:
            window = pl[hit.start(): hit.start() + 90]
            if not _NEG.search(window):
                return False, f"JD requires an advanced degree: '{term}'"
    # Experience requirement: must be in a "hard job requirement" context and not
    # negated by "not required"; exclude noise such as "30+ years of experience"
    # found in company profiles.
    _EXP1 = re.compile(
        r"(\d+)\s*\+?\s*years?'?\s*(?:of\s*)?experience\s+"
        r"(?:as a|as an|in|working|required|within)", re.I)
    _EXP2 = re.compile(
        r"(?:at least|minimum|require|must have|with at least)\s+"
        r"(\d+)\s*\+?\s*years?'?\s*(?:of\s*)?experience", re.I)
    _NEGEXP = re.compile(r"not required|no .{0,15}experience|experience (?:is )?not", re.I)
    m = _EXP1.search(pl) or _EXP2.search(pl)
    if m and not _NEGEXP.search(pl[max(0, m.start() - 50): m.start() + 80]):
        return False, "JD requires several years of experience"
    return True, f"JD ({src}) shows no hard experience / advanced-degree requirement"


# ---------------------------------------------------------------------------
# Link liveness verification
# ---------------------------------------------------------------------------
def verify(job: dict) -> None:
    live, note = fetch.is_live(job.get("official_link", ""))
    # A status code alone is not proof of life on a job board: an expired post is
    # served as HTTP 200 with a short "expired" template. Only board links need the
    # extra read, so official pages cost no additional request.
    if live and job.get("official_type") == "commercial_board":
        if fetch.page_says_expired(job.get("official_link", "")):
            live, note = False, "the page states the post has expired"
    job["verified_date"] = __import__("datetime").date.today().isoformat()
    if not live:
        job["status"] = "expired"
        job["notes"] = (job.get("notes", "") + f" Link verification failed: {note}").strip()
    else:
        job["status"] = "active"
        job["notes"] = (job.get("notes", "") + f" Link verified: {note}").strip()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def _dedupe_key(job: dict) -> str:
    return (job.get("title", "").strip().lower(), job.get("employer", "").strip().lower())


def run() -> list[dict]:
    raw = collect_all()
    print(f"[pipeline] raw jobs: {len(raw)}")

    seen = {}
    for job in raw:
        cat, cat_score = assign_category(job)
        job["category"] = cat
        job["category_name"] = config.CATEGORIES[cat]["name"]
        stars, reason = fit_score(job, cat_score)
        job["ai_edtech_fit"] = stars
        job["fit_reason"] = reason
        # Relevance gate (based on the title, to avoid department keywords
        # wrongly letting administrative roles through): if the title matches no
        # direction keyword and no role-relevance keyword, it is off-target.
        title_l = job.get("title", "").lower()
        cat_title_score = sum(
            1 for meta in config.CATEGORIES.values()
            for kw in meta["keywords"] if kw in title_l
        )
        rel_hit = any(k in title_l for k in config.RELEVANCE_KEYWORDS)
        if cat_title_score == 0 and not rel_hit:
            job["status"] = "excluded"
            job["excluded_reason"] = "No keyword match with the AI/EdTech/data/teaching directions"
            seen[_dedupe_key(job)] = job
            continue
        jd_text = _get_jd_text(job)
        keep, why = compliance_check(job, jd_text=jd_text)
        job["compliance_note"] = why
        if not keep:
            job["status"] = "excluded"
            job["excluded_reason"] = why
            seen[_dedupe_key(job)] = job
            continue
        # Description + tags (for the student page)
        job["description"] = _build_description(job, jd_text)
        job["tags"] = assign_tags(job)
        verify(job)
        k = _dedupe_key(job)
        if k in seen:
            continue
        seen[k] = job

    jobs = list(seen.values())
    # Sort: active first -> fit score -> sooner deadline first
    def sort_key(j):
        active = 0 if j.get("status") == "active" else 1
        stars = -(j.get("ai_edtech_fit", 0))
        dl = j.get("deadline") or "9999-12-31"
        return (active, stars, dl)
    jobs.sort(key=sort_key)

    active = [j for j in jobs if j.get("status") == "active"]
    print(f"[pipeline] kept {len(active)} active after compliance; "
          f"excluded / pending review: {len(jobs) - len(active)}")
    return jobs


if __name__ == "__main__":
    out = run()
    for j in out:
        print(f"[{j['status']}] ⭐{j['ai_edtech_fit']} {j['category']} "
              f"{j['title']} | {j['deadline']} | {j.get('compliance_note','')[:40]}")
