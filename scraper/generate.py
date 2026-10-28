"""
generate.py — Generates data/jobs.json (working copy), site/jobs.json (read directly
by GitHub Pages), site/index.html (student page, with tag filtering, embedded backup
data + runtime fetch of ./jobs.json), and REPORT.md (maintainer log, with filtering
details and Pages deployment notes).

The HTML contains only job metadata + official links + a short description; it does not
reproduce the full JD text, and contains no "filtered / pending-review" information
(that information is written only to REPORT.md for maintainers).
"""
from __future__ import annotations

import os
import sys
import json
import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SITE_DIR = os.path.join(ROOT, "site")
TODAY = datetime.date.today().isoformat()


def _clean(v):
    return v if v not in (None, "", "N/A") else None


def build_records(jobs: list[dict]) -> list[dict]:
    recs = []
    for j in jobs:
        recs.append({
            "title": j.get("title"),
            "employer": j.get("employer"),
            "department": j.get("department"),
            "category": j.get("category"),
            "category_name": j.get("category_name"),
            "location": j.get("location"),
            "degree": j.get("degree"),
            "experience": j.get("experience"),
            "ai_edtech_fit": j.get("ai_edtech_fit"),
            "fit_reason": j.get("fit_reason"),
            "tags": j.get("tags") or [],
            "description": j.get("description") or "",
            "discover_source": j.get("discover_source"),
            "official_link": j.get("official_link"),
            "official_type": j.get("official_type"),
            "posted_date": _clean(j.get("posted_date")),
            "deadline": _clean(j.get("deadline")),
            "verified_date": j.get("verified_date"),
            "status": j.get("status"),
            "compliance_note": j.get("compliance_note"),
            "excluded_reason": j.get("excluded_reason"),
            "notes": j.get("notes"),
        })
    return recs


def write_json(jobs: list[dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SITE_DIR, exist_ok=True)
    # data/jobs.json: full working copy (all statuses, for troubleshooting)
    full_payload = {
        "generated_at": TODAY,
        "target_audience": "EdUHK BSc(AI&EdTech) fresh graduates",
        "total_listed": sum(1 for j in jobs if j.get("status") == "active"),
        "jobs": build_records(jobs),
    }
    p1 = os.path.join(DATA_DIR, "jobs.json")
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, ensure_ascii=False, indent=2)
    # site/jobs.json: public copy read directly by GitHub Pages (active only,
    # in the same folder as the student page, ./jobs.json)
    active_jobs = [j for j in jobs if j.get("status") == "active"]
    site_payload = {
        "generated_at": TODAY,
        "target_audience": "EdUHK BSc(AI&EdTech) fresh graduates",
        "total_listed": len(active_jobs),
        "jobs": build_records(active_jobs),
    }
    p2 = os.path.join(SITE_DIR, "jobs.json")
    with open(p2, "w", encoding="utf-8") as f:
        json.dump(site_payload, f, ensure_ascii=False, indent=2)
    print(f"[generate] wrote {p1} and {p2}")
    return full_payload


def _stars(n: int) -> str:
    n = max(0, min(3, int(n or 0)))
    return "★" * n + "☆" * (3 - n)


def _esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _board_home(link: str) -> str:
    from urllib.parse import urlparse
    netloc = urlparse(link or "").netloc or "recruit.com.hk"
    return f"https://{netloc}/" if not netloc.startswith("http") else netloc


def render_html(jobs: list[dict]) -> str:
    records = build_records(jobs)
    active = [r for r in records if r.get("status") == "active"]
    active_json = json.dumps(active, ensure_ascii=False).replace("</", "<\\/")

    wl = "; ".join(config.UNIVERSITY_SOURCES.values()) + \
         "; and the Hong Kong Labour Department jobs.gov.hk"
    excl = ", ".join(sorted(config.EXCLUDED_DOMAINS))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hong Kong AI × EdTech Graduate Jobs · EdUHK BSc(AI&EdTech)</title>
<style>
  :root {{
    --bg:#f6f8fb; --card:#ffffff; --ink:#1f2933; --muted:#5b6b7b;
    --brand:#0b6bcb; --brand2:#0a4f9c; --line:#e2e8f0; --warn:#b45309; --ok:#15803d;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang HK","Microsoft YaHei",sans-serif;
         background:var(--bg); color:var(--ink); line-height:1.6; }}
  header {{ background:linear-gradient(135deg,var(--brand),var(--brand2)); color:#fff; padding:32px 20px; }}
  .wrap {{ max-width:1040px; margin:0 auto; }}
  header h1 {{ margin:0 0 6px; font-size:1.7rem; }}
  header p {{ margin:4px 0; opacity:.95; }}
  main {{ max-width:1040px; margin:0 auto; padding:24px 20px 60px; }}
  .sub {{ color:var(--muted); font-size:.9rem; margin:0 0 14px; }}
  .notice {{ background:#eaf2fc; border:1px solid #cfe2fb; color:#0a4f9c; padding:12px 16px; border-radius:10px; font-size:.9rem; margin:18px 0; }}
  .filter {{ display:flex; gap:8px; flex-wrap:wrap; margin:16px 0 20px; }}
  .fbtn {{ background:#fff; border:1px solid var(--line); color:var(--brand2); padding:6px 14px; border-radius:999px; cursor:pointer; font-size:.85rem; }}
  .fbtn.active {{ background:var(--brand); color:#fff; border-color:var(--brand); }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px; box-shadow:0 1px 2px rgba(16,24,40,.04); }}
  .card-head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }}
  .card-head h3 {{ margin:0; font-size:1.02rem; }}
  .fit {{ color:#f59e0b; font-size:1.05rem; white-space:nowrap; }}
  .src {{ display:inline-block; background:#eef2f7; color:var(--brand2); border:1px solid #d6e2f0;
         border-radius:999px; padding:1px 8px; font-size:.72rem; margin-top:2px; }}
  .meta {{ display:flex; flex-direction:column; gap:2px; margin:8px 0; font-size:.85rem; color:var(--muted); }}
  .tags {{ display:flex; gap:6px; flex-wrap:wrap; margin:8px 0; }}
  .tag {{ background:#e8f1fb; color:var(--brand2); border:1px solid #cfe2fb; border-radius:6px; padding:2px 8px; font-size:.75rem; }}
  .desc {{ font-size:.85rem; color:var(--ink); background:#f8fafc; border-left:3px solid var(--brand); padding:6px 10px; border-radius:0 8px 8px 0; margin:8px 0; }}
  .links {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:6px; }}
  .btn {{ text-decoration:none; font-size:.85rem; padding:7px 12px; border-radius:8px; }}
  .btn.primary {{ background:var(--brand); color:#fff; }}
  .btn.ghost {{ background:#eef2f7; color:var(--brand2); border:1px solid #d6e2f0; }}
  .empty {{ color:var(--muted); grid-column:1/-1; text-align:center; padding:30px; }}
  .panel {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; margin:24px 0; }}
  .panel h2 {{ margin-top:0; }}
  .redflags li {{ color:var(--warn); }}
  footer {{ text-align:center; color:var(--muted); font-size:.8rem; padding:24px; }}
  code {{ background:#eef2f7; padding:1px 5px; border-radius:4px; }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>Hong Kong AI × EdTech Graduate Job Board</h1>
    <p>For: final-year students of <b>BSc(AI&amp;EdTech)</b>, The Education University of Hong Kong (EdUHK) · only posts open to bachelor graduates / fresh graduates welcome</p>
    <p>Last updated: {TODAY} · links verified for liveness</p>
  </div>
</header>
<main>
  <p class="sub">Currently open: <b id="count">{len(active)}</b> jobs · Sources: university official vacancy pages, employer recruitment pages, and major Hong Kong job boards (JobsDB / CTgoodjobs / Recruit / CPjobs)</p>

  <div class="notice">
    ⚠️ This page only summarises publicly advertised <b>metadata, tags and a short description</b>; it does not reproduce the full job description. Please open the links to confirm the latest requirements, deadlines and how to apply. Links come in three kinds, all verified for liveness: an <b>official post</b> points to a named vacancy on the employer's or university's own site; a <b>recruitment page</b> is the employer's own page listing whatever posts are currently open, so read it for the current vacancies; a <b>job-board post</b> is discovered through a search service and expires sooner, so apply promptly and confirm with the official source.
  </div>

  <div class="filter" id="filter"><!-- tag filter buttons generated by script --></div>

  <div class="grid" id="grid"><!-- job cards generated by script --></div>

  <section class="panel">
    <h2>🛡️ Scam alerts (red flags)</h2>
    <ul class="redflags">
      <li>Asks for an upfront fee / deposit, or to buy products before starting</li>
      <li>Requests sensitive information such as ID card, bank account or passwords</li>
      <li>Contacts you only via a personal email (e.g. Gmail / 126) with no company domain</li>
      <li>Salary that is clearly off market (too high or too low)</li>
    </ul>
    <p>Cross-check: Hong Kong Scameter anti-scam search <a href="https://cyberdefender.hk/scameter/" target="_blank" rel="noopener">Scameter ↗</a></p>
  </section>

  <section class="panel">
    <h2>📋 Data sources and compliance</h2>
    <p><b>Allowed sources (whitelist):</b> {wl}.</p>
    <p><b>Excluded sources:</b> {excl} and other aggregator / scraping / blog sites (treated only as leads; included only after verification against the official source).</p>
    <p>This project is a non-commercial, education-purpose public information aggregation tool: it directly crawls only the official vacancy pages of universities and public data such as the Hong Kong Labour Department's jobs.gov.hk; commercial job boards are discovered through public search-engine indexing, links only (no bot scraping, no bypass of any verification); access is low-frequency and compliant with <code>robots.txt</code>, using an identifiable User-Agent with a contact email; only job metadata, tags and a short description are published, the full JD text is not reproduced, and no personal data is collected. For questions or takedown requests, contact {config.CONTACT_NAME} (<code>{config.CONTACT_EMAIL}</code>).</p>
  </section>
</main>
<footer>
  Generated by EdUHK-AIEdTech-JobBot · {TODAY} · for reference only; the employer / university official information prevails
</footer>

<script>
const FALLBACK = {active_json};
function esc(s){{ return String(s==null?'':s).replace(/[&<>"]/g, c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c])); }}
function stars(n){{ n=+n||0; return '★'.repeat(n)+'☆'.repeat(3-n); }}
function boardHome(link){{ try{{ return 'https://'+new URL(link).hostname+'/'; }}catch(e){{ return 'https://recruit.com.hk/'; }} }}
function cardHTML(j){{
  const tags=(j.tags||[]).map(t=>'<span class="tag">'+esc(t)+'</span>').join('');
  const isOff=j.official_type==='employer_official'||j.official_type==='employer_vacancy';
  const isPage=j.official_type==='employer_careers_page';
  const pLabel=isPage?'Recruitment page ↗':(isOff?'Official post ↗':'Job-board post ↗');
  const gLabel=isOff?'University vacancies ↗':'Job board ↗';
  const gHref=isOff?'https://eduhk.hk/en/current-openings':boardHome(j.official_link);
  const src='<span class="src">'+esc(j.discover_source||'')+'</span>';
  const desc=j.description?'<p class="desc">'+esc(j.description)+'</p>':'';
  const dl=isPage?'See the page for current openings':(j.deadline||'N/A (ongoing recruitment)');
  const dept=j.department?'<span>📂 '+esc(j.department)+'</span>':'';
  const ghost=isPage?'':'<a class="btn ghost" href="'+esc(gHref)+'" target="_blank" rel="noopener">'+gLabel+'</a>';
  return '<article class="card" data-tags="'+((j.tags||[]).map(esc).join(' '))+'">'
    +'<div class="card-head"><h3>'+esc(j.title)+'</h3><span class="fit" title="Fit rating">'+stars(j.ai_edtech_fit)+'</span></div>'
    +'<div class="meta"><span>🏛️ '+esc(j.employer)+'</span>'+dept+'<span>📍 '+esc(j.location||'')+'</span><span>⏰ Deadline: '+esc(dl)+'</span>'+src+'</div>'
    +'<div class="tags">'+tags+'</div>'+desc
    +'<div class="links"><a class="btn primary" href="'+esc(j.official_link)+'" target="_blank" rel="noopener">'+pLabel+'</a>'
    +ghost+'</div>'
    +'</article>';
}}
let ACTIVE=[]; let FILTER=new Set();
function allTags(list){{ const s=new Set(); list.forEach(j=>(j.tags||[]).forEach(t=>s.add(t))); return [...s].sort(); }}
function renderFilter(list){{
  const tags=allTags(list);
  let html='<button class="fbtn active" data-t="">All</button>';
  tags.forEach(t=>{{ html+='<button class="fbtn" data-t="'+esc(t)+'">'+esc(t)+'</button>'; }});
  const box=document.getElementById('filter'); box.innerHTML=html;
  box.querySelectorAll('.fbtn').forEach(b=>b.onclick=()=>{{
    const t=b.getAttribute('data-t');
    FILTER=new Set(t?[t]:[]);
    box.querySelectorAll('.fbtn').forEach(x=>x.classList.toggle('active', x.getAttribute('data-t')===t));
    renderGrid();
  }});
}}
function renderGrid(){{
  const list=ACTIVE.filter(j=>FILTER.size===0||(j.tags||[]).some(t=>FILTER.has(t)));
  document.getElementById('grid').innerHTML = list.map(cardHTML).join('') || '<p class="empty">No jobs under this tag yet.</p>';
  document.getElementById('count').textContent=list.length;
}}
function render(list){{
  ACTIVE=list.slice().sort((a,b)=>((+b.ai_edtech_fit||0)-(+a.ai_edtech_fit||0)) || ((a.deadline||'9')<(b.deadline||'9')?-1:1));
  renderFilter(ACTIVE); renderGrid();
}}
render(FALLBACK);
fetch('./jobs.json').then(r=>r.ok?r.json():Promise.reject()).then(d=>{{
  render((d.jobs||[]).filter(j=>j.status==='active'));
}}).catch(()=>{{ /* use embedded backup data for local file:// preview */ }});
</script>
</body>
</html>"""
    return html


def write_html(jobs: list[dict]):
    os.makedirs(SITE_DIR, exist_ok=True)
    html = render_html(jobs)
    path = os.path.join(SITE_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[generate] wrote {path}")
    return path


def write_report(jobs: list[dict]):
    """Generate the maintainer log REPORT.md (with filtering details and Pages notes)."""
    records = build_records(jobs)
    active = [r for r in records if r.get("status") == "active"]
    excluded = [r for r in records if r.get("status") != "active"]
    lines = []
    lines.append(f"# AIETJobs run report (maintainer view) · {TODAY}\n")
    lines.append("> This file is for maintainers only (includes filtering details). The student page `site/index.html` contains no filtered / pending-review information.\n")
    lines.append("- Target audience: EdUHK BSc(AI&EdTech) fresh graduates")
    lines.append(f"- Raw crawled: {len(records)} posts")
    lines.append(f"- **Shown on student page (active): {len(active)} posts**")
    lines.append(f"- Auto-filtered / pending review: {len(excluded)} posts\n")

    lines.append("## ✅ Jobs shown to students today\n")
    for j in active:
        tags = ", ".join(j.get("tags") or [])
        lines.append(f"- ⭐{j['ai_edtech_fit']} **{j['title']}** — {j['employer']}"
                     + (f" · {j['department']}" if j.get("department") else "")
                     + f" · tags: {tags}"
                     + f" · Deadline {j.get('deadline') or 'N/A'} · [{j['discover_source']}]({j['official_link']})")
    lines.append("")

    lines.append("## 🚫 Auto-filter reason breakdown (not shown to students; maintainers only)\n")
    c = Counter(j.get("excluded_reason", "") for j in excluded)
    if c:
        for reason, n in c.most_common():
            lines.append(f"- {n} posts: {reason}")
    else:
        lines.append("- None (all passed today)")
    lines.append("")

    lines.append("## ⚠️ To-do / notes\n")
    lines.append("- Commercial job boards (JobsDB / CTgoodjobs / Recruit / CPjobs) deep links expire in about 30 days and are re-discovered daily; currently they rely on manually recorded leads in `data/discovered.json` (no search API configured). Full automation is possible once a search API is connected.")
    lines.append("- The other 7 universities (HKU / CUHK / HKUST / PolyU / CityU / HKBU / Lingnan) ATS systems are mostly JS shells / certificate / gateway issues inside the sandbox and are not yet connected; `live.py` already has a framework, and connecting them will expand daily coverage.")
    lines.append("- All links pass the `is_live` liveness check; those that fail are marked `expired` and not shown to students.")
    lines.append("")

    lines.append("## 🚀 GitHub Pages deployment (let Pages read the data directly)\n")
    lines.append("The student page `site/index.html` calls `fetch('./jobs.json')` when loading:")
    lines.append("1. Use the repository's **`site/` directory** as the Pages source (`Settings → Pages → Build from a branch`, choose `main` and the `/site` folder).")
    lines.append("2. The generator writes the same data to both `site/jobs.json` and `site/index.html` (same folder), so on Pages `index.html` can read `./jobs.json` directly, and every commit updates the page.")
    lines.append("3. If publishing from the root, move the two files from `site/` to the repository root (relative paths stay the same).")
    lines.append("4. A local `file://` preview cannot fetch, so backup data is embedded; opening locally still shows the day's jobs.\n")

    lines.append("## Running\n")
    lines.append("```bash\npython -m scraper.run   # crawl -> filter -> generate site/ and REPORT.md\n```")
    lines.append("(Use the venv Python that includes pypdf: PDF description extraction depends on it.)")

    path = os.path.join(ROOT, "REPORT.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[generate] wrote {path}")
    return path


def generate(jobs: list[dict]):
    write_json(jobs)
    write_html(jobs)
    write_report(jobs)


if __name__ == "__main__":
    from pipeline import run
    generate(run())
