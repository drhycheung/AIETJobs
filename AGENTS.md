# AGENTS.md — Hong Kong AI × EdTech daily job-push system (handover / from-scratch rebuild guide)

> This document is a **self-contained handover specification**. If you are a newly assigned agent, reading this file alone lets you rebuild the entire system from scratch without relying on past conversations.
> Current status: a **working MVP** exists alongside one **created-but-unverified scheduled task**. The user decided to **rebuild from scratch**; this file is for the new agent to reference and rebuild (the existing code may be reused or discarded).

---

## 0. One-line goal

Build a **daily automated** system for **final-year BSc(AI&EdTech) students at The Education University of Hong Kong (EdUHK)** that crawls Hong Kong AI / EdTech related jobs → verifies official links → generates a **static website** → publishes it to **GitHub Pages**, for students to reference.

- Repository name (confirmed): **`AIETJobs`** (PascalCase, public repository, used for GitHub Pages)
- Target readers: **bachelor final-year students only**; reject posts that require experience / a licence / a Master's degree
- Deliverable: only a **static site** is placed on GitHub; no personal privacy data is stored

---

## 1. Hard constraints (must be strictly followed, non-negotiable)

### 1.1 Target audience
- Collect only posts that are **"open to bachelor graduates / fresh graduate welcome / experience is a plus, not required"**.
- Programmatically filter out: requiring X years of experience, requiring a professional licence, requiring a Master's or higher degree, already closed, dead link, non-Hong Kong, or not from a whitelisted source.

### 1.2 Information-source whitelist (two types; everything else is excluded)
**✅ Allowed:**
| Type | Sites |
|---|---|
| Major Hong Kong job boards | `jobs.gov.hk` (Labour Department official), JobsDB, CTgoodjobs, Recruit, CPjobs |
| Vacancy pages of all Hong Kong universities | HKU, CUHK, HKUST, PolyU, CityU, HKBU, Lingnan, EdUHK, HKSYU, etc. official recruitment systems |

**🚫 Explicitly excluded (aggregator / scraper / blog sites, never used):**
```
hiringcafe.com, joblum.com, careers.sh, bebee.com, hkese.net, offertoday.com,
thebigjobsite.com, postjobfree.com, indeed.com, linkedin.com, gradconnection.com,
jobfinder.com, hirelala.com, sigma.ai, imerit.com, glassdoor.com, ziprecruiter.com
```
> Rule: even if you spot a desirable post on one of those sites, treat it only as a lead and include it only after verifying it against the employer's official website / official ATS.

### 1.3 Core iron rule: discover via the whitelist, verify via the official source
- Jobs **must be discovered** from either the "major Hong Kong job boards" or the "vacancy pages of Hong Kong universities".
- The **final link shown to students must be the company / university official post** (official recruitment system / official school website), used to verify that the post **still exists**.
- **Do not rely long-term on board deep links that expire** (measured: JobsDB links go down in about 30 days; jobs.gov.hk detail pages use session tokens and deep links easily misredirect / expire). Board posts should be **re-discovered daily**, with the official link as the verification anchor.

### 1.4 Five job directions (categorisation and keyword system)
| # | Direction | Typical posts | Search keywords (Chinese / English, covering Cantonese phrasing) |
|---|---|---|---|
| ① | **AI / EdTech in universities** | RA, Learning Technology Developer, Educational Development Officer, Multimedia Developer | `Research Assistant AI education` / `Learning Technology` / `Educational Development` / `Multimedia Developer` |
| ② | **AI & EdTech industry** | EdTech company AI developer, Education Product Engineer | `EdTech developer` / `AI education` / `教育科技` / `AI 教學` |
| ③ | **Pure AI / ML** | AI/ML Engineer, Data Science Trainee, Algorithm roles | `AI Engineer` / `Machine Learning` / `Data Science Graduate Trainee` / `NLP GenAI` |
| ④ | **Teaching / promoting AI in schools** | AI Teaching Assistant, STEM/IT Teacher, School ETO, **PGDE pathway** | `AI 教學助理` / `STEM Instructor` / `IT Teacher` / `Education Technology Officer` / `PGDE` |
| ⑤ | **Data analysis / processing / annotation** | Data Analyst, Data Processing Officer, Data Annotator | `Data Analyst fresh graduate` / `Data Processing` / `Data Annotation 數據標註` / `語音轉錄標註` |

> Keywords use **Chinese + English + common Cantonese phrasing** (e.g. `數據標註`, `教學助理`, `教學`) to cover local recruitment language.

### 1.5 Fit-rating priority
- Score by the EdUHK BSc(AI&EdTech) competency profile as **⭐ (1–3 stars)**: ML/NLP/CV, intelligent tutoring, learning technology, EdTech, Python, and education-internship background are prioritised; university / same-field posts are prioritised.
- Bonus keywords: `ai, artificial intelligence, machine learning, nlp, computer vision, education, educational, edtech, learning, teaching, stem, python, multimedia, data, language, smart`.

---

## 2. Compliance and ethics red lines (the life-or-death line for a public repository, never cross)

The repository is **public**, so everything must be "defensible in public":

1. **Never bypass human verification (CAPTCHA)**: commercial boards are only "discovered" through public search-engine indexing and a link is provided; **never script against their verification**.
2. **Never evade IP bans**: **do not enable proxies / IP rotation** to bypass bans; rely on low frequency + rate limiting + an identifiable UA to naturally avoid being blocked.
3. **Comply with `robots.txt` and each site's Terms of Service**: parse before crawling; skip when a forbidden path is matched.
4. **Identifiable access identity**: a fixed UA with a contact email, transparent and contactable. Example:
   ```
   EdUHK-AIEdTech-JobBot/1.0 (+https://github.com/drhycheung/AIETJobs; contact: hyincheung@eduhk.hk)
   ```
5. **Low frequency, low load**: once per day, very few requests per site, random intervals between requests; impose no perceptible burden on servers.
6. **Copyright**: publish **only metadata + links** (job title / employer / location / degree / experience / deadline), **never copy the full JD body**.
7. **Collect no personal data** (recruiter contact details, applicant data, or other PDPO-personal information); process only publicly advertised information.
8. **Opt-out**: the README carries a contact email; if any site owner requests takedown, immediately exclude that source and delete the related data.
9. **Quality red line**: any post that is "likely dead / unverifiable / hits a compliance prohibition" should be **withheld for the day or flagged ⚠️ pending review** rather than pushed as a dead link, fake post or violating content.

### Public README compliance statement (recommended to keep verbatim)
```
This project is a non-commercial, education-purpose public information aggregation
tool serving final-year BSc(AI&EdTech) students at The Education University of Hong Kong. We:
- crawl directly only the official vacancy pages of universities and public data such as
  the Hong Kong Labour Department's jobs.gov.hk;
- discover commercial job-board posts through public search-engine indexing, providing
  links only, never bot-scraping and never bypassing any verification;
- access at low frequency, comply with robots.txt, use an identifiable User-Agent with a
  contact email;
- publish only job metadata and links, never the full JD text, and collect no personal data;
- respect copyright and the wishes of each site, and honour takedown requests immediately.
For questions or takedown requests, contact: <email>
```

---

## 3. Recommended technical architecture (two scheduling options, see section 6 for trade-offs)

```
[1 Discovery] University official vacancy pages + jobs.gov.hk: direct crawl (low-frequency, compliant)
          Commercial job boards: discovered through search-engine indexing -> post URL (no direct scrape, no verification bypass)
   ↓
[2 Parsing] Extract fields (title / employer / location / degree / experience / AI attributes / posted date / deadline / original link)
   ↓
[3 Official verification] For each employer, find the official post on the official website / official ATS -> confirm the post still exists
            Not found -> official homepage + official email, labelled "no self-hosted official post"
   ↓
[4 Compliance filter] Remove: requires experience / licence / Master's, already closed, dead link, non-Hong Kong, non-whitelist, robots forbidden, personal-data type
   ↓
[5 Sorting] Star rating by fit, university / same-field posts first; deduplicate
   ↓
[6 Generation] Markdown (source) + HTML (GitHub Pages template, metadata + links only)
   ↓
[7 Publishing] Push to GitHub Pages (gh-pages branch)
   ↓
[8 Logging] Record dead links, items newly removed today, verification failures -> retrospective tuning
```

**Technology selection advice**
- Language: **Python 3.11**
- Official-page crawling: `requests` (**force IPv4**, see section 5 pitfalls) + `BeautifulSoup`
- JS-render fallback: Playwright **only for "rendering official pages"**, **never for bypassing CAPTCHA**
- Search discovery: a search API (Google Programmable Search free quota / Bing / SerpAPI) or free search-engine HTML (pitfall: search-engine direct connections inside the sandbox often time out)
- Compliance: `urllib.robotparser` to parse robots + identifiable UA + per-site rate limiting
- Storage: `jobs.json` (current day) + `archive/` (historical archive, for trend and dedupe)
- Template: Jinja2 to render HTML
- Publishing: git push -> `gh-pages` -> GitHub Pages

**Data model (fields per job)**
```
title, employer, category (①–⑤), category_name, location,
degree, experience, ai_edtech_fit (⭐×1-3), fit_reason,
discover_source, official_link, official_type,
posted_date, deadline, verified_date, status (active|expired|unknown), notes
```
> Use **JSON** as intermediate storage, then render Markdown and HTML. **Published content contains only the metadata and links in the table above; the full JD is not embedded.**

---

## 4. Existing MVP (reference implementation; keep or discard)

A working implementation exists inside the sandbox, files under `/workspace`:

```
scraper/
  config.py        # whitelist, excluded domains, university official pages, five-direction keywords, UA, PUSH_GITHUB switch
  fetch.py         # fetch_url (force IPv4 + proxy fallback) / search_discover (search discovery, board links only)
  pipeline.py      # run(queries, seeds) -> dedupe + scoring + filter
  live.py          # collect() actually crawls university official pages (PolyU/HKBU/CUHK/HKUST/EdUHK)
  verify.py        # is_live(url) liveness check
  generate.py      # generate site/index.html + data/jobs.json + data/daily-report.md
  deploy.py        # push() gated by PUSH_GITHUB + GH_TOKEN (not triggered during review period)
  run.py           # entry: pipeline.run -> generate -> deploy per switch
  seeds.json       # 6 pre-verified real jobs (fallback)
site/index.html    # generated static site
data/jobs.json     # current-day data
README.md          # compliance statement + deployment guide
design-methodology-architecture.md  # methodology and architecture (V2 compliant edition, must-read)
verification-report.md              # verification record that scheduling is executable + real data is obtainable
```

> MVP measured: manually running `python3.11 run.py` generates 7 jobs (4 of them from real university official vacancy pages), and correctly stops at "do not push to GitHub" during the review period.

---

## 5. Pitfall list / lessons learned (avoid these when rebuilding)

1. **Aggregator sites / wrong links**: BYTEWISE's jobs.gov.hk token link jumped to a massage advert; HKUST Interfolio link was dead; `ph.jobstreet.com` is the Philippines edition (not Hong Kong) — **always replace the final link with the employer / university official post**.
2. **Sandbox Python direct connection**: Python can directly reach `jobs.gov.hk`, `cuhk.taleo.net`, `polyu`, `hkust` (200), but **university sites' IPv6 direct connections often fail -> force IPv4** (`requests` adapter `family=socket.AF_INET`, or `curl -4`).
3. **Search-discovery timeouts**: DuckDuckGo / Bing HTML inside the sandbox often hang for 3+ minutes -> use **short timeouts + fail fast**, never retry to the point of dragging down the daily task.
4. **live_collect returns 0**: network jitter + swallowed exceptions caused silent failure -> add logging, explicit exceptions, retry with backoff.
5. **Bad titles**: JS-rendered pages captured navigation text like "Description" / "Breadcrumb" -> add a `_JOB_WORDS` keyword filter; JS pages fall back to the **pre-verified TARGET title**.
6. **GitHub authentication**: POST to github.com inside the sandbox **times out** (GET works), device-code OAuth is unavailable -> GitHub write operations are handed to the **cloud runtime / a user-provided PAT (repo scope)**; do not force OAuth inside the sandbox.
7. **JobsDB 30-day expiry**: board deep links cannot be stored long-term; they must be **re-discovered daily**, with the official link as the anchor.
8. **Some small/medium EdTech firms have no self-hosted official post** (e.g. eClass, Popular e-Learning, BYTEWISE): the official site only has a brand page -> provide only "official homepage + official email" and **label it honestly**.
9. **Quality over coverage**: after giving up direct scraping / verification bypass, commercial-board coverage is lower than full direct scraping — this is the trade-off bought by compliance and is acceptable (university pages and jobs.gov.hk remain stable direct-crawl fallbacks).

---

## 6. Scheduling trade-offs (the key decision point for this rebuild)

The original methodology recommended **GitHub Actions** (daily cron triggers the script + deploys gh-pages), on the grounds that the sandbox / local machine cannot be "always on", while Actions provides free, stable daily compute.

> ⚠️ **Legacy issue from this round (to be decided by the new agent)**: a **WorkBuddy cloud scheduled task** was created once (task ID `13622729`, Cron `0 0 8 * * *` Asia/Shanghai, 08:00 HKT daily, no GitHub push during the review period), but the user reported "something seems wrong there". That task may be unstable or unverified.
> **Recommendation**: the new agent should first evaluate returning to **GitHub Actions** native scheduling (more controllable, co-located with GitHub Pages, no extra PAT injection into a third-party scheduler), or use WorkBuddy scheduling only after confirming it actually works. Either way, **during the review period do not push to GitHub; let the user observe for a few days before setting `PUSH_GITHUB=1`**.

### Steps to deploy to GitHub (execute after the user provides a PAT)
1. Create the public repository **`AIETJobs`** (user habit: capitalise the first letter of each word, no hyphen).
2. Configure deployment credentials: `GH_TOKEN` (repo scope), `GH_OWNER` (username), `PUSH_GITHUB=1`.
3. Push the static site to `gh-pages` (or `main` with Pages pointing to `/site` / `docs`), and enable GitHub Pages.
4. Publish the compliance statement in the README (see section 2).

---

## 7. To-do list (hand to the next agent)

- [ ] Decide on scheduling: GitHub Actions (recommended) or fix the WorkBuddy scheduled task.
- [ ] Rebuild / complete the crawler (9+ university adapters + jobs.gov.hk, compliant direct crawl).
- [ ] Rebuild the search-discovery module (call a search API to find commercial-board post URLs, no direct scrape, no verification bypass).
- [ ] Official-link parsing and liveness check (404 / Expired detection).
- [ ] Compliance filter + ⭐ scoring + sorting + deduplication.
- [ ] GitHub Pages template (five-direction sections, ⭐, dual links, anti-scam and compliance sections).
- [ ] `.github/workflows/daily.yml` (if Actions is chosen): daily cron discovery + verification + deployment.
- [ ] Run end-to-end once, output the day's report, confirm official-page crawl / search discovery / verification are feasible.
- [ ] **Review period**: do not push first; let the user observe for a few days; only create the repository + enable push after confirmation.
- [ ] Provide "deploy to your own GitHub repository" instructions + a README compliance-statement template.

### Anti-scam safeguards (written into a fixed page section)
- Red flags: upfront fee / deposit, requesting ID or bank details, personal-email contact, salary clearly off market.
- Cross-check: Hong Kong Scameter anti-scam search https://cyberdefender.hk/scameter/
- The page explicitly shows the whitelist, exclusion list and compliance statement, inviting oversight.

---

## 8. Known to-be-confirmed / placeholder items

| Item | Current value | Note |
|---|---|---|
| Contact email | `hyincheung@eduhk.hk` (Dr. HY Cheung) | configured in `scraper/config.py` (`CONTACT_EMAIL`) and shown in the README and on the site |
| Repository URL | `https://github.com/drhycheung/AIETJobs` | public repository, live at https://drhycheung.github.io/AIETJobs/ |
| `GH_OWNER` | `drhycheung` | repository owner |
| `GH_TOKEN` | not in repository | deployment uses the Actions built-in `GITHUB_TOKEN` (repo scope not needed) |
| `PUSH_GITHUB` | `True` | review period over; the site is deployed automatically by `.github/workflows/deploy.yml` on every push to `main` |

> ⚠️ Any configuration containing secrets (`GH_TOKEN`) **must not enter the public repository**; inject it only via environment variables / Secrets.
