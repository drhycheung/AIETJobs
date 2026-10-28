# AIETJobs run report (maintainer view) · 2026-10-28

> This file is for maintainers only (includes filtering details). The student page `site/index.html` contains no filtered / pending-review information.

- Target audience: EdUHK BSc(AI&EdTech) fresh graduates
- Raw crawled: 72 posts
- **Shown on student page (active): 14 posts**
- Auto-filtered / pending review: 58 posts

## ✅ Jobs shown to students today

- ⭐3 **Research Assistant II** — The Education University of Hong Kong (EdUHK) · Centre for Learning, Teaching and Technology · tags: University, Fresh-graduate friendly · Deadline 03 Nov 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35042/RAII_LTTC_2600894.pdf)
- ⭐2 **Multimedia Developer** — The Education University of Hong Kong (EdUHK) · Faculty of Education and Human Development · tags: Multimedia, University, Fresh-graduate friendly · Deadline 04 Nov 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35050/PO_ProjA_FEHD_2600928.pdf)
- ⭐2 **Teaching Assistant** — The Education University of Hong Kong (EdUHK) · Department of Curriculum and Instruction · tags: Teaching, University, Fresh-graduate friendly · Deadline 29 Oct 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35022/TAsst_C%26I_2600918.pdf)
- ⭐2 **加入我們 Careers｜Edcosys 雲智未來｜AI 教育公司** — www.edcosys.com · tags: Artificial Intelligence, Teaching, Industry, Fresh-graduate friendly · Deadline N/A · [Tavily search](https://www.edcosys.com/careers)
- ⭐2 **Graduate STEM Developer - Hong Kong** — dataintellect.com · tags: Artificial Intelligence, Industry, Fresh-graduate friendly · Deadline N/A · [Tavily search](https://dataintellect.com/join-us/job?smid=743999909655143)
- ⭐1 **Research Assistant I** — The Education University of Hong Kong (EdUHK) · Department of Psychology · tags: University, Fresh-graduate friendly · Deadline 04 Nov 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35092/RAI_PS_2600923.pdf)
- ⭐1 **Research Assistant I/II (Part-time)** — The Education University of Hong Kong (EdUHK) · Department of Social Sciences and Policy Studies · tags: University, Intern / Trainee, Fresh-graduate friendly · Deadline 06 Nov 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35073/RAI_RAII_SSPS_2600932.pdf)
- ⭐1 **EDU A.I. 人才招聘** — www.eduai.org · tags: Artificial Intelligence, Industry, Fresh-graduate friendly · Deadline N/A · [Tavily search](https://www.eduai.org/about-us/career)
- ⭐1 **官立中學及小學非公務員職位空缺 - 教育局** — www.edb.gov.hk · tags: Teaching, Industry, Fresh-graduate friendly · Deadline N/A · [Tavily search](https://www.edb.gov.hk/tc/about-edb/info/recruitment/NCSC-Vacancy/Index_NCSC.html)
- ⭐1 **AI 教學助理一名- 蘇浙公學** — jobs.ctgoodjobs.hk · tags: Artificial Intelligence, Educational Technology, Teaching, Industry, Fresh-graduate friendly · Deadline N/A · [Tavily search](https://jobs.ctgoodjobs.hk/job/10283496/ai-%E6%95%99%E5%AD%B8%E5%8A%A9%E7%90%86%E4%B8%80%E5%90%8D)
- ⭐1 **Software Engineering Graduate Programme in Hong Kong** — careers.fdmgroup.com · tags: Industry, Fresh-graduate friendly · Deadline N/A · [Tavily search](https://careers.fdmgroup.com/vacancies/839/software-engineering-graduate-programme.html)
- ⭐1 **Data Engineering Graduate Programme  in Hong Kong - FDM Group** — careers.fdmgroup.com · tags: Industry, Fresh-graduate friendly · Deadline N/A · [Tavily search](https://careers.fdmgroup.com/vacancies/2541/data-engineering-graduate-programme.html)
- ⭐1 **Software Engineering Graduate Programme │ International students│Hong Kong based  in Hong Kong - FDM Group** — careers.fdmgroup.com · tags: Industry, Intern / Trainee, Fresh-graduate friendly · Deadline N/A · [Tavily search](https://careers.fdmgroup.com/vacancies/1721/software-engineering-graduate-programme--international-students-hong-kong-based.html)
- ⭐1 **IT Intern (Programming) (Part-time)** — The Education University of Hong Kong (EdUHK) · Office of the Chief Information Officer · tags: University, Intern / Trainee, Fresh-graduate friendly · Deadline N/A · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/32500/SH_OCIO_2501246.pdf)

## 🚫 Auto-filter reason breakdown (not shown to students; maintainers only)

- 40 posts: No keyword match with the AI/EdTech/data/teaching directions
- 12 posts: Academic/faculty post (usually requires a PhD): 'professor'
- 4 posts: Academic/faculty post (usually requires a PhD): 'head of'
- 2 posts: Negative title keyword

## ⚠️ To-do / notes

- Commercial job boards (JobsDB / CTgoodjobs / Recruit / CPjobs) deep links expire in about 30 days and are re-discovered daily; currently they rely on manually recorded leads in `data/discovered.json` (no search API configured). Full automation is possible once a search API is connected.
- The other 7 universities (HKU / CUHK / HKUST / PolyU / CityU / HKBU / Lingnan) ATS systems are mostly JS shells / certificate / gateway issues inside the sandbox and are not yet connected; `live.py` already has a framework, and connecting them will expand daily coverage.
- All links pass the `is_live` liveness check; those that fail are marked `expired` and not shown to students.

## 🚀 GitHub Pages deployment (let Pages read the data directly)

The student page `site/index.html` calls `fetch('./jobs.json')` when loading:
1. Use the repository's **`site/` directory** as the Pages source (`Settings → Pages → Build from a branch`, choose `main` and the `/site` folder).
2. The generator writes the same data to both `site/jobs.json` and `site/index.html` (same folder), so on Pages `index.html` can read `./jobs.json` directly, and every commit updates the page.
3. If publishing from the root, move the two files from `site/` to the repository root (relative paths stay the same).
4. A local `file://` preview cannot fetch, so backup data is embedded; opening locally still shows the day's jobs.

## Running

```bash
python -m scraper.run   # crawl -> filter -> generate site/ and REPORT.md
```
(Use the venv Python that includes pypdf: PDF description extraction depends on it.)